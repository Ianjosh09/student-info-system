export const KEY='ianjosh09.sis.web.v1';
export function validateRecord(input){
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Each student must be a JSON object.');
 const record={};
 for(const key of ['student_id','name','course','email']){
  if(typeof input[key]!=='string')throw Error(`${key.replace('_',' ')} must be text.`);
  const value=input[key].trim();
  if(!value||value.length>150||/[\x00-\x1f]/.test(value))throw Error(`${key.replace('_',' ')} must contain 1–150 valid characters.`);
  record[key]=value;
 }
 if(!/^[A-Za-z0-9_-]{1,30}$/.test(record.student_id))throw Error('Student ID must contain 1–30 letters, numbers, hyphens or underscores.');
 for(const [key,min,max] of [['age',1,120],['year_level',1,6]]){
  if(typeof input[key]!=='number'||!Number.isInteger(input[key])||input[key]<min||input[key]>max)throw Error(`${key.replace('_',' ')} must be a whole number from ${min} to ${max}.`);
  record[key]=input[key];
 }
 if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(record.email))throw Error('Enter a valid email address.');
 return record;
}
export function validateRecords(input){
 if(!Array.isArray(input))throw Error('JSON must be a list of student records.');
 if(input.length>10000)throw Error('Please import no more than 10,000 students.');
 const ids=new Set();
 return input.map(item=>{const r=validateRecord(item),id=r.student_id.toLowerCase();if(ids.has(id))throw Error(`Duplicate student ID: ${r.student_id}`);ids.add(id);return r;});
}
export function loadState(storage){
 const raw=storage.getItem(KEY);
 if(raw===null)return {records:[],previous:null,saved:null};
 const data=JSON.parse(raw);
 return {records:validateRecords(data.records),previous:data.previous===null?null:validateRecords(data.previous),saved:typeof data.saved==='string'?data.saved:null};
}
export function saveState(storage,current,records){
 const next={records:validateRecords(records),previous:current.records,saved:new Date().toISOString()};
 // One write keeps the records and their previous version together.
 storage.setItem(KEY,JSON.stringify(next));
 return next;
}
export function csv(records){
 const fields=['student_id','name','age','course','year_level','email'];
 const cell=value=>{let text=String(value);if(/^[\s]*[=+@-]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';};
 return [fields.join(','),...records.map(r=>fields.map(key=>cell(r[key])).join(','))].join('\r\n');
}
