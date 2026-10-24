# Copyright (c) 2026 Subhanjan Das. MIT.
# AI-assisted with OpenAI Codex; generated replay fragments retain upstream notices.
"""Build existing public inputs; never certify a new QRH bound or issue admission."""
from pathlib import Path
import argparse,hashlib,json,subprocess
PIN='0ce80fdddebb03128d30a917006d8520e7a774b8'
p=argparse.ArgumentParser();p.add_argument('--trusted-checkout',type=Path,required=True);args=p.parse_args()
root=args.trusted_checkout.resolve()
actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
assert actual==PIN,('Unexpected verifier revision',actual)
original=(root/'verifier/standard/replay.py').read_text()
prefix=original.split("stage('compile standard candidate')")[0]
assert prefix!=original
assert prefix.count('budget_seconds=10800')==1
assert prefix.count('args = parser.parse_args()')==1
prefix=prefix.replace('budget_seconds=10800','budget_seconds=18000')
prefix=prefix.replace('args = parser.parse_args()', "parser.add_argument('--input-roots', type=Path, required=True)\nparser.add_argument('--cache-out', type=Path, required=True)\nargs = parser.parse_args()")
compiler=original[original.index('module_started = {}'):original.index('# Legacy contracts used a sequential order')]
assert 'v.sandboxed_run' in compiler and 'publish_module' in compiler
finish=r'''
# Compile only existing public Submissions modules. No proposed Candidate module
# enters the output, and no new result is marked accepted by this helper.
roots=json.loads(args.input_roots.read_text())
needed=set()
def include(name):
    assert name.startswith('Submissions.'), name
    if name in needed:return
    needed.add(name)
    for parent in contract['module_dependencies'][name]:include(parent)
for name in roots:include(name)
order=[name for name in contract['build_order'] if name in needed]
dependencies={name:contract['module_dependencies'][name] for name in order}
assert len(order)==len(needed) and all(set(ds)<=needed for ds in dependencies.values())
subset={**contract,'build_order':order,'module_dependencies':dependencies,
 'source_files':{'src/'+name.replace('.','/')+'.lean':contract['source_files']['src/'+name.replace('.','/')+'.lean'] for name in order}}
import threading
completed=set()
completion_lock=threading.Lock()
original_compile_one=compile_one
def tracked_compile_one(name,count):
    original_compile_one(name,count)
    with completion_lock:completed.add(name)
failure=None
try:
    compile_modules(order,dependencies,tracked_compile_one,jobs=jobs,
      is_memory_error=lambda error:isinstance(error,v.ResourceExhausted) and 'result oom-kill)' in str(error))
except Exception as error:
    failure=error
# The scheduler has joined active workers. Keep only successfully returned
# compilations; partial output from a failed compiler can never enter the cache.
assert all(set(dependencies[name])<=completed for name in completed)
v.verify_tool_snapshot(tools)
assert sha(work/'exports/Challenge.export')==challenge_hash
assert inputs=={str(path.relative_to(source)):sha(path) for path in source.rglob('*') if path.is_file()}
check_libraries()
from standard.build_cache import pack_cache
import tempfile
out=args.cache_out.resolve();out.mkdir(parents=True,exist_ok=True)
cache_inputs=build_inputs(subset,profile,library_inventory,approved_tools)
# Already-restored baseline objects remain available from the official signed cache.
additional=[name for name in order if name in completed and name not in cached_modules]
shards=[];current=[];current_bytes=0
for name in additional:
    rel=name.replace('.','/')
    products=[Path(str(work/'candidate-lib'/rel)+suffix) for suffix in ['.olean','.olean.private','.olean.server']]
    assert products[0].is_file()
    size=sum(path.stat().st_size for path in products if path.exists())
    assert size<2*1024**3,('Oversized individual input',name)
    if current and current_bytes+size>2*1024**3:
        shards.append(current);current=[];current_bytes=0
    current.append(name);current_bytes+=size
if current:shards.append(current)
archives=[]
for index,names in enumerate(shards):
    with tempfile.TemporaryDirectory(dir=out,prefix='pack-') as tmp:
        stage=Path(tmp)
        for name in names:
            rel=name.replace('.','/')
            for suffix in ['.olean','.olean.private','.olean.server']:
                src=Path(str(work/'candidate-lib'/rel)+suffix)
                if src.exists():
                    assert src.is_file() and not src.is_symlink()
                    dst=Path(str(stage/rel)+suffix);dst.parent.mkdir(parents=True,exist_ok=True)
                    os.link(src,dst)
        selected={**cache_inputs,'modules':{name:cache_inputs['modules'][name] for name in names}}
        archive=out/f'public-inputs-{index:03}.tar.gz'
        pack_cache(stage,archive,selected)
        archives.append({'file':archive.name,'sha256':sha(archive),'modules':len(names),'bytes':archive.stat().st_size})
upstream_root=Path(__file__).resolve().parents[2]
notice_out=out/'provenance';notice_out.mkdir(exist_ok=True)
for filename in ['LICENSE','NOTICE']:
    path=upstream_root/filename
    if path.is_file():shutil.copyfile(path,notice_out/(filename+'.txt'))
for owner in ['lewko-acyclic-bootstrap-874772906','openai-baseline']:
    path=upstream_root/'submissions'/owner/'metadata.json'
    if path.is_file():shutil.copyfile(path,notice_out/(owner+'-metadata.json'))
(out/'input-contract.json').write_text(json.dumps(subset,sort_keys=True)+'\n')
(out/'cache-inputs.json').write_text(json.dumps(cache_inputs,sort_keys=True)+'\n')
report={'status':'COMPILED_PUBLIC_INPUTS_ONLY' if failure is None else 'PARTIAL_PUBLIC_INPUTS','new_bound_verified':False,'official_admission':False,
 'source_commit':contract['head_sha'],'source_repository':contract['repository'],
 'modules_required':len(order),'modules_compiled':len(completed),'failure':str(failure) if failure else None,'restored_official_cache_modules':len(needed&cached_modules),
 'newly_compiled_modules':len(additional),'environment':cache_inputs['environment'],
 'source_compiler':approved_tools['source_lean'],'tools':approved_tools,
 'roots':roots,'archives':archives,'sandbox_controls':'PASS',
 'final_candidate_kernels':'NOT RUN; the proposed candidate is not part of this job',
 'changes_to_upstream_driver':'Source-only dependency subset; shared deadline increased from 3h to 5h; no statement, axiom, tool, kernel or sandbox policy relaxed.'}
(out/'input-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
if failure is not None:raise failure
'''
program=prefix+"stage('compile existing public inputs only')\njobs = threads\n"+compiler+finish
compile(program,'generated-public-input-builder.py','exec')
output=root/'verifier/standard/generated-public-input-builder.py';output.write_text(program)
print(json.dumps({'driver':str(output),'trusted_revision':PIN,'generated_sha256':hashlib.sha256(program.encode()).hexdigest()}))
