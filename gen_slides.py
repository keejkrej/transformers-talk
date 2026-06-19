import json, math, os

W, H = 960, 540
GAP = 450
START_X, Y = 100, 100

# palette (pastel bg / darker stroke)
BLUE_BG, BLUE_ST = "#e7f5ff", "#1971c2"
BLUE_LITE = "#d0ebff"
GREEN_BG, GREEN_ST = "#e6fcf5", "#0ca678"
VIOLET_BG, VIOLET_ST = "#f3f0ff", "#6741d9"
ORANGE_BG, ORANGE_ST = "#fff4e6", "#e8590c"
YELLOW_BG, YELLOW_ST = "#fff9db", "#f08c00"
RED_BG, RED_ST = "#fff5f5", "#fa5252"
GRAY_BG, GRAY_ST = "#f1f3f5", "#868e96"
INK, SUB = "#1e1e1e", "#495057"

def sx(i): return START_X + (i - 1) * (W + GAP)

def frame(i, name, notes):
    return {"type":"frame","tempId":f"s{i}","name":name,
            "x":sx(i),"y":Y,"width":W,"height":H,
            "customData":{"presenterNotes":notes}}

def title(i, t, size=34, y=40, color=INK, fam=7):
    return {"type":"text","x":sx(i)+56,"y":Y+y,"width":W-112,"height":size+12,
            "text":t,"fontSize":size,"fontFamily":fam,"strokeColor":color,"frameId":f"s{i}"}

def cap(i, t, x=56, y=H-80, w=W-112, size=16, color=SUB, fam=5):
    return {"type":"text","x":sx(i)+x,"y":Y+y,"width":w,"height":size*2+8,
            "text":t,"fontSize":size,"fontFamily":fam,"strokeColor":color,"frameId":f"s{i}"}

def txt(i, x, y, w, h, t, size=18, fam=5, color=INK):
    return {"type":"text","x":sx(i)+x,"y":Y+y,"width":w,"height":h,
            "text":t,"fontSize":size,"fontFamily":fam,"strokeColor":color,"frameId":f"s{i}"}

def rect(tid, i, x, y, w, h, bg, st, label=None, lsize=18, lfam=7, rough=1):
    e={"type":"rectangle","tempId":tid,"x":sx(i)+x,"y":Y+y,"width":w,"height":h,
       "backgroundColor":bg,"strokeColor":st,"fillStyle":"solid","roughness":rough,
       "roundness":{"type":3},"frameId":f"s{i}"}
    if label: e["label"]={"text":label,"fontSize":lsize,"fontFamily":lfam}
    return e

def ell(tid, i, x, y, w, h, bg, st, label=None, lsize=18, lfam=7, rough=1):
    e={"type":"ellipse","tempId":tid,"x":sx(i)+x,"y":Y+y,"width":w,"height":h,
       "backgroundColor":bg,"strokeColor":st,"fillStyle":"solid","roughness":rough,
       "frameId":f"s{i}"}
    if label: e["label"]={"text":label,"fontSize":lsize,"fontFamily":lfam}
    return e

def arr(i, x, y, pts, start=None, end=None, stroke=INK, head="arrow", rough=1):
    a={"type":"arrow","x":sx(i)+x,"y":Y+y,"width":pts[-1][0],"height":pts[-1][1],
       "points":pts,"endArrowhead":head,"roughness":rough,"strokeColor":stroke,"frameId":f"s{i}"}
    if start: a["startBinding"]={"elementId":start[0],"fixedPoint":start[1],"mode":"inside"}
    if end:   a["endBinding"]={"elementId":end[0],"fixedPoint":end[1],"mode":"inside"}
    return a

def line(i, x, y, pts, stroke=INK, rough=1, width=2):
    return {"type":"line","x":sx(i)+x,"y":Y+y,"width":pts[-1][0],"height":pts[-1][1],
            "points":pts,"roughness":rough,"strokeColor":stroke,"strokeWidth":width,
            "frameId":f"s{i}"}

slides = {}

# 1 — Title (single hero block)
i=1; s=[]
s.append(frame(i,"Title",
    "* Welcome. Today's paper: Vaswani et al., 2017 (NeurIPS).\n"
    "* It introduces the Transformer — the first sequence model built only on attention.\n"
    "* This single paper reshaped NLP and underpins every modern LLM."))
s.append(txt(i,56,170,W-112,70,"Attention Is All You Need",size=52,fam=7))
# accent underline
s.append(line(i,56,250,[[0,0],[W-112,0]],stroke=BLUE_ST,rough=1,width=3))
s.append(txt(i,56,278,W-112,80,
    "Vaswani · Shazeer · Parmar · Uszkoreit · Jones · Gomez · Kaiser · Polosukhin\nGoogle Brain / Research — NeurIPS 2017",
    size=17,fam=5,color=SUB))
s.append(txt(i,56,H-90,W-112,40,"arxiv.org/abs/1706.03762",size=16,fam=8,color=GRAY_ST))
slides[i]=s

# 2 — Recurrence is sequential (one chain)
i=2; s=[]
s.append(frame(i,"Recurrence is sequential",
    "* Pre-2017 sequence models (RNN/LSTM/GRU) compute hidden states one step at a time.\n"
    "* Each state h_t depends on h_{t-1} — so you cannot process the sequence in parallel.\n"
    "* This sequential dependency is the bottleneck the paper attacks."))
s.append(title(i,"Recurrence is sequential"))
cells=5; cx0=80; cy=230; cw=120; ch=100; step=170
hids=[]
for j in range(cells):
    tid=f"r{j}"; hids.append(tid)
    s.append(rect(tid,i,cx0+j*step,cy,cw,ch,GRAY_BG,GRAY_ST,
        label=f"h{j+1}",lsize=24,lfam=7))
    s.append(txt(i,cx0+j*step,cy+ch+12,cw,28,f"x{j+1}",size=16,fam=8,color=SUB))
# sequential arrows h_j -> h_{j+1}
for j in range(cells-1):
    s.append(arr(i,cx0+j*step+cw,cy+ch/2,[[0,0],[step-cw,0]],
        start=(hids[j],[1,0.5]),end=(hids[j+1],[0,0.5]),stroke=RED_ST,head="arrow"))
# "wait" label
s.append(txt(i,cx0+cells*step-cw+30,cy+10,140,30,
    "wait",size=16,fam=5,color=RED_ST))
s.append(cap(i,"each step waits on the last — no parallelism across the sequence",size=15))
slides[i]=s

# 3 — Self-attention: everything sees everything (complete directed graph)
i=3; s=[]
s.append(frame(i,"Self-attention: everything sees everything",
    "* Self-attention lets every position look at every other position in a single step.\n"
    "* Constant path length between any pair — long-range dependencies become easy.\n"
    "* Fully parallelizable across positions, which is exactly what GPUs exploit."))
s.append(title(i,"Self-attention: everything sees everything",size=30))
nodes=6; nx0=120; ny=270; nw=96; nh=80; nstep=142
nids=[]
for j in range(nodes):
    tid=f"n{j}"; nids.append(tid)
    bg = YELLOW_BG if j==2 else BLUE_BG
    st = ORANGE_ST if j==2 else BLUE_ST
    s.append(ell(tid,i,nx0+j*nstep,ny,nw,nh,bg,st,
        label=f"x{j+1}",lsize=20,lfam=7))
# query token x3 attends to every token (including itself)
q=nids[2]
qa=(nx0+2*nstep+nw/2, ny+nh/2)
for b in range(nodes):
    if b==2: continue
    cb_c=(nx0+b*nstep+nw/2, ny+nh/2)
    dx=cb_c[0]-qa[0]
    bow = -120 if b!=2 else 0
    pts=[[0,0],[dx/2,bow],[dx,0]]
    s.append(arr(i,qa[0],qa[1],pts,
        start=(q,[0.5,0.5]),end=(nids[b],[0.5,0.5]),
        stroke=ORANGE_ST,head="arrow",rough=1))
s.append(txt(i,nx0+2*nstep-10,ny-44,260,28,
    "this token attends to every token",size=16,fam=5,color=ORANGE_ST))
s.append(cap(i,"one step · the same is true for every other token in the sequence"))
slides[i]=s

# 4 — Scaled dot-product attention (single pipeline + formula)
i=4; s=[]
s.append(frame(i,"Scaled dot-product attention",
    "* Attention maps a query Q to key-value pairs (K,V): output is a weighted sum of values.\n"
    "* Weights = softmax( Q·Kᵀ ), scaled by 1/√d_k to keep gradients stable when d_k is large.\n"
    "* This is the one operation the entire architecture is built from."))
s.append(title(i,"Scaled dot-product attention",size=32))
s.append(rect("f4",i,56,108,W-112,60,YELLOW_BG,YELLOW_ST,
    "Attention(Q, K, V) = softmax( Q·Kᵀ / √d_k ) · V",lsize=22,lfam=8,rough=0))
boxes=[("Q, K, V",BLUE_BG,BLUE_ST),("MatMul",GRAY_BG,GRAY_ST),
       ("Scale\n×1/√d_k",YELLOW_BG,YELLOW_ST),("Softmax",GREEN_BG,GREEN_ST),
       ("× V",VIOLET_BG,VIOLET_ST)]
bx0=56; by=240; bw=150; bh=88; step=180
bids=[]
for j,(lab,bg,st) in enumerate(boxes):
    tid=f"a{j}"; bids.append(tid)
    s.append(rect(tid,i,bx0+j*step,by,bw,bh,bg,st,label=lab,lsize=17,lfam=7,rough=0))
for j in range(len(bids)-1):
    s.append(arr(i,bx0+j*step+bw,by+bh/2,[[0,0],[step-bw,0]],
        start=(bids[j],[1,0.5]),end=(bids[j+1],[0,0.5]),stroke=INK,rough=0))
s.append(cap(i,"dot-products give similarity → softmax gives weights → multiply by values",y=H-70))
slides[i]=s

# 5 — Multi-head: parallel views (fan-out / fan-in)
i=5; s=[]
s.append(frame(i,"Multi-head: parallel views",
    "* Instead of one attention on d_model, run h=8 heads in parallel on d_k=d_v=64.\n"
    "* Each head can learn a different relationship (e.g. syntactic vs semantic).\n"
    "* Concatenate the heads and project back to d_model=512."))
s.append(title(i,"Multi-head: parallel views",size=34))
# input node
s.append(ell("in5",i,56,260,90,70,BLUE_BG,BLUE_ST,label="input",lsize=17,lfam=7))
heads=4; hx0=320; hy=180; hw=130; hh=58; vstep=72
hids=[]
for j in range(heads):
    tid=f"hd{j}"; hids.append(tid)
    s.append(rect(tid,i,hx0,hy+j*vstep,hw,hh,BLUE_LITE,BLUE_ST,
        label=f"head {j+1}",lsize=17,lfam=7,rough=0))
# concat
s.append(rect("cat5",i,560,210,140,70,GREEN_BG,GREEN_ST,
    label="Concat",lsize=18,lfam=7,rough=0))
# linear + out
s.append(rect("lin5",i,740,210,140,50,VIOLET_BG,VIOLET_ST,
    label="Linear",lsize=17,lfam=7,rough=0))
s.append(rect("out5",i,740,290,140,50,ORANGE_BG,ORANGE_ST,
    label="output",lsize=17,lfam=7,rough=0))
# input -> each head (elbow)
for j,hid in enumerate(hids):
    yp=hy+j*vstep+hh/2
    s.append(arr(i,146,295,[[0,0],[320-146,yp-295]],
        start=("in5",[1,0.5]),end=(hid,[0,0.5]),stroke=GRAY_ST,rough=0))
# each head -> concat (elbow right)
for j,hid in enumerate(hids):
    yp=hy+j*vstep+hh/2
    s.append(arr(i,hx0+hw,yp,[[0,0],[560-(hx0+hw),210+35-yp]],
        start=(hid,[1,0.5]),end=("cat5",[0,0.5]),stroke=GRAY_ST,rough=0))
# concat -> linear -> out
s.append(arr(i,700,225,[[0,0],[40,0]],start=("cat5",[1,0.5]),end=("lin5",[0,0.5]),stroke=INK,rough=0))
s.append(arr(i,810,260,[[0,0],[0,30]],start=("lin5",[0.5,1]),end=("out5",[0.5,0]),stroke=INK,rough=0))
s.append(txt(i,56,H-80,300,30,"h = 8 heads · d_k = d_v = 64 · d_model = 512",size=15,fam=8,color=SUB))
slides[i]=s

# 6 — Positional encoding (waves)
i=6; s=[]
s.append(frame(i,"Positional encoding",
    "* Self-attention is permutation-invariant — it has no sense of order.\n"
    "* Add a sinusoidal encoding to the embeddings so positions are distinguishable.\n"
    "* Sines/cosines of different frequencies let the model attend by relative position."))
s.append(title(i,"Positional encoding",size=36))
# build sine/cosine waves as polylines
import math
def wave(amp, freq, phase, yoff, kind="sin", steps=80, x0=80, x1=W-80, ybase=320):
    pts=[]
    for k in range(steps+1):
        t=k/steps
        xx=(x1-x0)*t
        fn=math.sin if kind=="sin" else math.cos
        yy=yoff - amp*fn(freq*xx*0.05+phase)
        pts.append([round(xx,1),round(yy-ybase,1)])
    return pts
# We'll place waves relative to a local origin at (x0, ybase). line() uses sx(i)+x.
# Use absolute local coords: origin (x0=80,ybase=320)
x0=80; ybase=320
def line_wave(i, pts, stroke, width=2):
    return {"type":"line","x":sx(i)+x0,"y":Y+ybase,"width":pts[-1][0],"height":(max(p[1] for p in pts)-min(p[1] for p in pts)),
            "points":pts,"roughness":1,"strokeColor":stroke,"strokeWidth":width,"frameId":f"s{i}"}
s.append(line_wave(i, wave(70,1,0,0,"sin"),"#1971c2",3))      # low freq sine
s.append(line_wave(i, wave(40,4,1.2,0,"cos"),"#e8590c",2))     # higher freq cos
s.append(line_wave(i, wave(28,8,2.4,0,"sin"),"#6741d9",2))     # high freq sine
# axis baseline
s.append(line(i,x0-10,ybase,[[0,0],[W-80-x0+10,0]],stroke=GRAY_ST,rough=1,width=1))
s.append(txt(i,56,150,W-112,40,
    "PE(pos,2i)=sin(pos/10000^(2i/d))    PE(pos,2i+1)=cos(pos/10000^(2i/d))",
    size=18,fam=8,color=INK))
s.append(txt(i,80,460,220,24,"sin · low freq",size=14,fam=5,color=BLUE_ST))
s.append(txt(i,300,460,220,24,"cos · mid freq",size=14,fam=5,color=ORANGE_ST))
s.append(txt(i,540,460,220,24,"sin · high freq",size=14,fam=5,color=VIOLET_ST))
s.append(cap(i,"added to input embeddings to inject order"))
slides[i]=s

# 7 — Architecture (encoder-decoder sketch)
i=7; s=[]
s.append(frame(i,"The Transformer architecture",
    "* Encoder: N=6 identical layers, each = self-attention + positionwise FFN, with residual+LayerNorm.\n"
    "* Decoder: N=6 layers, each = masked self-attention + cross-attention (K,V from encoder) + FFN.\n"
    "* Masking keeps positions from attending to the future; cross-attention reads the encoder output."))
s.append(title(i,"The Transformer architecture",size=30))
# ENCODER column
ex=120; ew=170
s.append(txt(i,ex,150,ew,28,"Encoder ×6",size=18,fam=7,color=BLUE_ST))
s.append(rect("enc_emb",i,ex,190,ew,52,BLUE_LITE,BLUE_ST,label="Input Embed + PE",lsize=14,lfam=7,rough=0))
s.append(rect("enc_sa",i,ex,258,ew,52,BLUE_BG,BLUE_ST,label="Self-Attention",lsize=14,lfam=7,rough=0))
s.append(rect("enc_ffn",i,ex,326,ew,52,GRAY_BG,BLUE_ST,label="Feed-Forward",lsize=14,lfam=7,rough=0))
s.append(arr(i,ex+ew/2,242,[[0,0],[0,16]],start=("enc_emb",[0.5,1]),end=("enc_sa",[0.5,0]),stroke=INK,rough=0))
s.append(arr(i,ex+ew/2,310,[[0,0],[0,16]],start=("enc_sa",[0.5,1]),end=("enc_ffn",[0.5,0]),stroke=INK,rough=0))
# DECODER column
dx=560; dw=170
s.append(txt(i,dx,150,dw,28,"Decoder ×6",size=18,fam=7,color=ORANGE_ST))
s.append(rect("dec_emb",i,dx,190,dw,52,ORANGE_BG,ORANGE_ST,label="Output Embed + PE",lsize=14,lfam=7,rough=0))
s.append(rect("dec_msa",i,dx,258,dw,52,"#fff5f5",RED_ST,label="Masked Self-Attn",lsize=14,lfam=7,rough=0))
s.append(rect("dec_ca",i,dx,326,dw,52,VIOLET_BG,VIOLET_ST,label="Cross-Attention",lsize=14,lfam=7,rough=0))
s.append(rect("dec_ffn",i,dx,394,dw,52,GRAY_BG,ORANGE_ST,label="Feed-Forward",lsize=14,lfam=7,rough=0))
s.append(rect("dec_out",i,dx,462,dw,0 if False else 0,0,0,0)) # ignore
# remove bogus; redo dec arrows
s.pop()
for a,b in [("dec_emb","dec_msa"),("dec_msa","dec_ca"),("dec_ca","dec_ffn")]:
    ya = 190 if a=="dec_emb" else (258 if a=="dec_msa" else 326)
    ha = 52
    s.append(arr(i,dx+dw/2,ya+ha,[[0,0],[0,16]],start=(a,[0.5,1]),end=(b,[0.5,0]),stroke=INK,rough=0))
# output head
s.append(rect("head",i,dx,462,dw,52,YELLOW_BG,YELLOW_ST,label="Linear + Softmax",lsize=14,lfam=7,rough=0))
s.append(arr(i,dx+dw/2,446,[[0,0],[0,16]],start=("dec_ffn",[0.5,1]),end=("head",[0.5,0]),stroke=INK,rough=0))
# encoder output -> cross attention
s.append(arr(i,ex+ew,352,[[0,0],[dx-(ex+ew),326-352+26]],
    start=("enc_ffn",[1,0.5]),end=("dec_ca",[0,0.5]),stroke=BLUE_ST,rough=0))
s.append(txt(i,ex+ew+10,300,90,24,"K, V",size=13,fam=8,color=BLUE_ST))
slides[i]=s

# 8 — Results (metric callouts)
i=8; s=[]
s.append(frame(i,"Results",
    "* WMT 2014 English→German: 28.4 BLEU — over 2 BLEU better than the previous best (incl. ensembles).\n"
    "* WMT 2014 English→French: 41.8 BLEU — a new single-model state of the art.\n"
    "* Trained in just 3.5 days on 8 GPUs — a fraction of the cost of prior best models."))
s.append(title(i,"Results",size=40))
s.append(rect("m1",i,56,170,270,180,GREEN_BG,GREEN_ST,
    "28.4 BLEU\nEN → DE\n(+2 over best)",lsize=26,lfam=7,rough=0))
s.append(rect("m2",i,345,170,270,180,BLUE_BG,BLUE_ST,
    "41.8 BLEU\nEN → FR\n(single-model SOTA)",lsize=24,lfam=7,rough=0))
s.append(rect("m3",i,634,170,270,180,ORANGE_BG,ORANGE_ST,
    "3.5 days\n8 GPUs\ntraining cost",lsize=26,lfam=7,rough=0))
s.append(cap(i,"state of the art on two translation benchmarks, at a fraction of the training cost"))
slides[i]=s

# 9 — Why it matters (one statement + chips)
i=9; s=[]
s.append(frame(i,"Why it matters",
    "* The Transformer dropped recurrence, making sequence models parallel and scalable.\n"
    "* This became the base architecture for BERT, GPT, T5, ViT and essentially all modern LLMs.\n"
    "* 'Attention is all you need' turned out to be one of the most consequential ideas in AI."))
s.append(title(i,"Why it matters",size=40))
s.append(rect("core",i,150,210,660,110,VIOLET_BG,VIOLET_ST,
    "The foundation of every modern LLM",lsize=30,lfam=7,rough=0))
chips=["BERT","GPT","T5","ViT","ChatGPT","Gemini"]
cx0=80; cy=380; cw=130; ch=54; step=145
for j,c in enumerate(chips):
    s.append(rect(f"c{j}",i,cx0+j*step,cy,cw,ch,BLUE_LITE,BLUE_ST,
        label=c,lsize=18,lfam=7,rough=0))
s.append(cap(i,"one idea, one paper, a decade of AI that followed",y=H-70))
slides[i]=s

os.makedirs("/tmp/slides",exist_ok=True)
for i,s in slides.items():
    with open(f"/tmp/slides/slide{i}.json","w") as f:
        json.dump(s,f,indent=None)
    print(f"slide {i}: {len(s)} elements")
print("done")