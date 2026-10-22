import argparse
import csv
import json
from pathlib import Path
import matplotlib.pyplot as plt
from models import Vehicle, Ship
from state import State
from result import SearchResult
from visualize import save_all, finish, plot_base, BLUE, ORANGE, GREEN
def restore(d, vehicles, ship):
    def state(s):
        obj=State(vehicles,ship,{k:(p['x'],p['y'],p['orient']) for k,p in s['inside'].items()})
        if not obj.is_valid() or obj.value()!=s['value']:
            raise ValueError('State JSON tidak valid atau value tidak cocok')
        return obj
    return SearchResult(d['name'],d['params'],state(d['initial_state']),state(d['final_state']),
                        d['history'],d['iterations'],d['duration_sec'],d['extras'])


def build(out):
    out=Path(out)
    data=json.loads((out/'instance.json').read_text())
    vehicles=[Vehicle(**v) for v in data['vehicles']];ship=Ship(**data['ship'])
    records=[];summary=[]
    for folder in ('hc','sa','ga'):
        for p in sorted((out/folder).glob('*.json')):
            d=json.loads(p.read_text()); res=restore(d,vehicles,ship)
            save_all(res,plot_base(p))
            records.append((p,d))
            summary.append(dict(label=d['label'],algorithm=d['name'],run=d['run_id'],
                params=json.dumps(d['params']),initial_value=d['initial_value'],final_value=d['final_value'],
                iterations=d['iterations'],duration_sec=d['duration_sec'],valid=d['final_state']['valid'],
                file=p.relative_to(out).as_posix()))
            if d['name']=='sa':
                with p.with_name(p.stem+'_trace.csv').open('w',newline='') as f:
                    writer=csv.DictWriter(f,fieldnames=list(d['extras']['trace'][0]));writer.writeheader();writer.writerows(d['extras']['trace'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    if summary:
        with (out/'summary.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    sa=[d for _,d in records if d['name']=='sa']
    if sa:
        fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
        labels=[f"Run {d['run_id']}" for d in sa]
        for d,label in zip(sa,labels):axs[0,0].plot(d['history'],label=label,lw=1,alpha=.8)
        axs[0,0].set(title='SA | objective tiga run',xlabel='Iterasi',ylabel='ShippingFee (juta)');axs[0,0].legend()
        pos=list(range(len(sa)))
        axs[0,1].bar([i-.18 for i in pos],[d['final_value'] for d in sa],width=.36,label='Akhir',color=BLUE)
        axs[0,1].bar([i+.18 for i in pos],[d['extras']['best_value'] for d in sa],width=.36,label='Terbaik',color=ORANGE)
        axs[0,1].set(xticks=pos,xticklabels=labels,title='Nilai akhir dan terbaik',ylabel='ShippingFee (juta)');axs[0,1].legend()
        for ax,key,title,ylabel in [(axs[1,0],'duration_sec','Durasi pencarian (tanpa plotting)','Detik'),(axs[1,1],'stuck_count','Episode stagnasi (proxy stuck)','Jumlah episode')]:
            vals=[d.get(key,d['extras'].get(key)) for d in sa]
            bars=ax.bar(labels,vals,color=GREEN);ax.bar_label(bars,fmt='%.3f' if key=='duration_sec' else '%d',padding=3)
            ax.set(title=title,ylabel=ylabel,ylim=(0,max(vals)*1.2+0.01))
        finish(fig,out/'plots/sa_perbandingan_3_run.png')
    groups={}
    for _,d in records:groups.setdefault(d['label'],[]).append(d)
    if groups:
        labels=list(groups)
        fig,axs=plt.subplots(2,1,figsize=(13,9),layout='constrained')
        for ax,key,title,ylabel in [(axs[0],'final_value','Hasil akhir per konfigurasi (titik = run)','ShippingFee (juta)'),(axs[1],'duration_sec','Durasi per konfigurasi; lingkungan run dapat berbeda','Detik')]:
            for i,label in enumerate(labels):
                vals=[d[key] for d in groups[label]]
                ax.bar(i,sum(vals)/len(vals),color=BLUE,alpha=.3)
                ax.scatter([i+(j-(len(vals)-1)/2)*.08 for j in range(len(vals))],vals,color=BLUE,s=25,zorder=3)
            ax.set(xticks=range(len(labels)),xticklabels=[l.replace('_','\n') for l in labels],title=title,ylabel=ylabel)
            ax.grid(axis='y',alpha=.2)
        finish(fig,out/'plots/perbandingan_konfigurasi.png')
    print(f'Visualisasi selesai: {len(records)} hasil run; {len(list(out.rglob("*.png")))} PNG.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(Path(__file__).resolve().parents[1]/'output'))
    build(parser.parse_args().out)
