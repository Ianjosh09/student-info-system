import {loadState,saveState,validateRecords,csv} from './records.mjs';
const $=id=>document.getElementById(id),form=$('student-form');
let state,storage,editing=null,toastTimer,pending=null;
function toast(message){$('toast').textContent=message;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,5000);}
function errorMessage(error){return error.name==='QuotaExceededError'?'Storage is full. Download a backup and free browser space. No change was saved.':error.message;}
function confirmAction(title,message,action){pending=action;$('confirm-title').textContent=title;$('confirm-text').textContent=message;$('confirm-dialog').showModal();$('confirm-cancel').focus();}
$('confirm-cancel').onclick=()=>$('confirm-dialog').close();
$('confirm-dialog').addEventListener('close',()=>{pending=null;});
$('confirm-ok').onclick=()=>{const action=pending;$('confirm-dialog').close();try{action?.();}catch(error){toast(errorMessage(error));}};
function commit(records,message){const next=saveState(storage,state,records);state=next;render();toast(message);}
function make(tag,text,className){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;}
function render(){
 const q=$('search').value.trim().toLowerCase(),year=$('year-filter').value;
 const visible=state.records.filter(r=>(!year||String(r.year_level)===year)&&[r.name,r.student_id,r.course,r.email].some(v=>v.toLowerCase().includes(q)));
 $('total').textContent=state.records.length;$('count').textContent=state.records.length;
 $('courses').textContent=new Set(state.records.map(r=>r.course.toUpperCase())).size;
 $('saved').textContent=state.saved?new Date(state.saved).toLocaleString(undefined,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'No changes yet';
 $('restore').disabled=state.previous===null;$('rows').replaceChildren();
 for(const r of visible){
  const tr=make('tr'),student=make('td'),wrap=make('div',undefined,'student-cell'),avatar=make('span',r.name.split(/\s+/).slice(0,2).map(s=>s[0]).join('').toUpperCase(),'avatar'),details=make('div');
  details.append(make('strong',r.name),make('small',r.email));wrap.append(avatar,details);student.append(wrap);tr.append(student,make('td',r.student_id));
  const course=make('td');course.append(make('span',r.course,'course-pill'));tr.append(course,make('td',`Year ${r.year_level}`),make('td',r.age));
  const actions=make('td'),buttons=make('div',undefined,'row-actions'),edit=make('button','Edit'),remove=make('button','Delete','delete');
  edit.setAttribute('aria-label',`Edit ${r.name}`);remove.setAttribute('aria-label',`Delete ${r.name}`);
  edit.onclick=()=>openForm(r);remove.onclick=()=>confirmAction('Delete student?',`Remove ${r.name} (${r.student_id}) from this browser? You can undo this until your next change.`,()=>commit(state.records.filter(s=>s.student_id!==r.student_id),'Student deleted.'));
  buttons.append(edit,remove);actions.append(buttons);tr.append(actions);$('rows').append(tr);
 }
 $('empty').hidden=visible.length>0;
 $('empty-title').textContent=state.records.length?'No matching students':'Your directory starts here';
 $('empty-text').textContent=state.records.length?'Try a different search or year level.':'Add your first student to bring this workspace to life.';
 $('empty-add').hidden=state.records.length>0;$('result-count').textContent=`Showing ${visible.length} of ${state.records.length} students`;
}
function openForm(record=null){
 editing=record?.student_id??null;form.reset();$('form-error').hidden=true;$('form-title').textContent=record?'Edit student':'Add student';
 for(const key of ['student_id','name','age','course','year_level','email'])form.elements.namedItem(key).value=record?.[key]??'';
 form.elements.namedItem('student_id').readOnly=!!record;$('student-dialog').showModal();form.elements.namedItem(record?'name':'student_id').focus();
}
$('add').onclick=()=>openForm();$('empty-add').onclick=()=>openForm();
$('close-form').onclick=$('cancel-form').onclick=()=>$('student-dialog').close();
form.onsubmit=event=>{event.preventDefault();try{
 const r=Object.fromEntries(new FormData(form));r.age=Number(r.age);r.year_level=Number(r.year_level);if(editing)r.student_id=editing;
 const records=editing?state.records.map(s=>s.student_id===editing?r:s):[...state.records,r];
 commit(records,editing?'Student updated.':'Student added.');$('student-dialog').close();
 }catch(error){$('form-error').textContent=errorMessage(error);$('form-error').hidden=false;}};
$('search').oninput=render;$('year-filter').onchange=render;
function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type})),link=make('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('backup').onclick=()=>download('students.json',JSON.stringify(state.records,null,2),'application/json');
$('csv').onclick=()=>download('students.csv',csv(state.records),'text/csv;charset=utf-8');
$('restore').onclick=()=>confirmAction('Undo last change?','Replace current records with the previous saved version. This can undo an add, edit, delete or import.',()=>commit(state.previous,'Previous version restored.'));
$('import').onclick=()=>$('file').click();
$('file').onchange=async()=>{const file=$('file').files[0];$('file').value='';if(!file)return;try{
 if(file.size>5*1024*1024)throw Error('Choose a JSON backup smaller than 5 MB.');
 const records=validateRecords(JSON.parse(await file.text()));
 confirmAction('Import student records?',`Replace your current ${state.records.length} records with ${records.length} records from this JSON file? Download a backup first if you want a separate copy.`,()=>commit(records,'JSON records imported.'));
 }catch(error){toast(error instanceof SyntaxError?'That file is not valid JSON.':errorMessage(error));}};
function boot(){try{storage=window.localStorage;state=loadState(storage);render();}catch(error){$('fatal').textContent='Unable to read browser records. Existing data has not been overwritten. Check browser storage permissions or try another browser. '+errorMessage(error);$('fatal').hidden=false;$('empty').hidden=true;document.querySelectorAll('main button,main input,main select').forEach(el=>el.disabled=true);}}
// Refresh other tabs so a later edit uses the latest saved list.
window.addEventListener('storage',event=>{if(event.storageArea===storage){$('student-dialog').close();$('confirm-dialog').close();boot();toast('Records refreshed from another tab.');}});
boot();
