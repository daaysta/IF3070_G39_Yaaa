"""Plot hasil SearchResult; koordinat x=kolom, y=baris, titik asal kiri atas."""
from pathlib import Path
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from state import get_dim

plt.rcParams.update({'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.titleweight': 'bold'})
BLUE, ORANGE, GREEN = '#1d4e89', '#d87628', '#2a9d8f'


def plot_base(json_path):
    p = Path(json_path).resolve()
    return str(p.parent.parent / 'plots' / p.parent.name / p.stem)

def finish(fig, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_objective(result, path):
    fig, ax = plt.subplots(figsize=(9, 4.5), layout='constrained')
    avg = result.extras.get('avg_history')
    ax.plot(result.history, color=GREEN if avg else BLUE,
            label='Maksimum populasi' if avg else 'State saat ini', linewidth=1.2)
    if avg:
        ax.plot(avg, color=ORANGE, label='Rata-rata populasi')
    if 'best_history' in result.extras:
        ax.plot(result.extras['best_history'], color=ORANGE, label='Terbaik sejauh ini')
    ax.set(xlabel='Generasi' if avg else 'Iterasi (0 = awal)', ylabel='ShippingFee (juta rupiah)',
           title=f'{result.name.upper()} | objective terhadap iterasi')
    ax.grid(alpha=.2); ax.legend()
    finish(fig, path)


def draw_deck(ax, state, title):
    ax.set(xlim=(0, state.ship.w), ylim=(state.ship.l, 0), xlabel='x (kolom)', ylabel='y (baris)')
    ax.set_aspect('equal')
    ax.set_xticks(range(state.ship.w+1)); ax.set_yticks(range(state.ship.l+1))
    colors = plt.get_cmap('tab20')
    for i, (vid, p) in enumerate(state.placements.items()):
        if p is None:
            continue
        x,y,o = p; dx,dy = get_dim(state.vehicles[vid],o)
        ax.add_patch(Rectangle((x,y),dx,dy,facecolor=colors(i%20),edgecolor='#334155',lw=1.3,alpha=.85))
        ax.text(x+dx/2,y+dy/2,f'{vid}\n{o}',ha='center',va='center',fontsize=8)
    ax.grid(alpha=.18)
    ax.set_title(f'{title}\nFee {state.value()} | berat {state.total_weight}/{state.ship.max_capacity}\n'
                 f'Di dalam {len(state.inside_ids())} | di luar {len(state.outside_ids())} | valid {state.is_valid()}',fontsize=10)


def gambar_state(state, path, judul):
    outside = state.outside_ids()
    fig, axes = plt.subplots(1,2,figsize=(11,max(7,len(outside)*.25+2)),
                             gridspec_kw={'width_ratios':[1,1.25]},layout='constrained')
    draw_deck(axes[0],state,judul)
    axes[1].axis('off')
    rows = [[vid,f'{state.vehicles[vid].w} x {state.vehicles[vid].l}',
             state.vehicles[vid].fee,state.vehicles[vid].weight] for vid in outside]
    if rows:
        table=axes[1].table(cellText=rows,colLabels=['ID','w x l','Fee (juta)','Berat'],
                            cellLoc='center',loc='center')
        table.auto_set_font_size(False);table.set_fontsize(9);table.scale(1,1.45)
    else:
        axes[1].text(.5,.5,'Semua kendaraan diangkut',ha='center')
    axes[1].set_title('Kendaraan di luar kapal\nTidak memiliki koordinat geladak',fontsize=11)
    finish(fig,path)


def plot_sa(result, base):
    tr=result.extras.get('trace',[])
    if not tr:
        return
    xs=[r['iteration'] for r in tr]
    fig,axs=plt.subplots(2,1,figsize=(10,7),sharex=True,layout='constrained')
    # Untuk delta <= 0, exp(delta/T) adalah probabilitas penerimaan (bias default 0).
    down=[r for r in tr if r['delta'] is not None and r['delta']<0]
    axs[0].scatter([r['iteration'] for r in down],[r['probability'] for r in down],s=10,alpha=.5,color=BLUE,label='Proposal menurun')
    chosen=[r for r in down if r['accepted']]
    axs[0].scatter([r['iteration'] for r in chosen],[r['probability'] for r in chosen],s=22,color=ORANGE,label='Menurun, diterima')
    axs[0].set(ylim=(-.03,1.05),ylabel='Probabilitas',title='SA | probabilitas penerimaan proposal menurun')
    axs[0].legend();axs[0].grid(alpha=.2)
    axs[1].plot(xs,[r['temperature'] for r in tr],color=GREEN)
    axs[1].set(yscale='log',xlabel='Iterasi',ylabel='Temperatur (log)',title='Jadwal pendinginan');axs[1].grid(alpha=.2)
    finish(fig,base+'_probabilitas_suhu.png')
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    axs[0].plot(xs,[r['stagnation_length'] for r in tr],color=BLUE)
    axs[0].axhline(result.params['stuck_window'],color=ORANGE,ls='--',label='Ambang episode stuck')
    for r in tr:
        if r['stuck_event']:axs[0].axvline(r['iteration'],color=ORANGE,alpha=.4)
    axs[0].set(xlabel='Iterasi',ylabel='Iterasi tanpa best baru',title=f"Stagnasi | {result.extras['stuck_count']} episode")
    axs[0].legend(fontsize=8)
    counts=[sum(r['accepted'] and r['delta']>0 for r in tr),sum(r['accepted'] and r['delta']==0 for r in tr),
            len(chosen),sum(r['delta'] is not None and not r['accepted'] for r in tr),sum(r['delta'] is None for r in tr)]
    bars=axs[1].bar(['Naik','Setara','Turun','Ditolak','Tanpa\nproposal'],counts,color=[GREEN,BLUE,ORANGE,'#94a3b8','#cbd5e1'])
    axs[1].bar_label(bars,padding=3);axs[1].set_ylim(0,max(counts)*1.18+1)
    axs[1].set(ylabel='Jumlah iterasi',title='Keputusan penerimaan')
    finish(fig,base+'_stagnasi_keputusan.png')


def save_all(result, base):
    plot_objective(result,base+'_objective.png')
    gambar_state(result.initial_state,base+'_awal.png','State awal')
    gambar_state(result.final_state,base+'_akhir.png','State akhir (current terakhir)')
    if result.name=='sa':
        plot_sa(result,base)
        from state import State
        d=result.extras['best_state']
        best=State(result.initial_state.vehicles,result.initial_state.ship,
                   {v:(p['x'],p['y'],p['orient']) for v,p in d['inside'].items()})
        gambar_state(best,base+'_terbaik.png','State terbaik sepanjang pencarian')
