# M0 literature verification: reference values

Compiled 2026-11-20. Every value below was read from the arXiv text (TeX source or PDF) of the
cited paper. Table and equation numbers follow the **arXiv version** (counted from the LaTeX
source); journal numbering may differ. "derived" = arithmetic done by us from the quoted
inputs. "unverified" = could not be confirmed from a primary source.

---

## 1. PACS-CS N_f = 2+1 ensembles (arXiv:0807.1661, PRD 79, 034503)

**Common setup** (Sec. II.A–B)

| Quantity | Value | Source |
|---|---|---|
| Gauge action | Iwasaki, c1 = −0.331, c0 = 3.648 | 0807.1661 Sec. II.A |
| Quark action | NP O(a)-improved Wilson-clover | Sec. II.A |
| β | 1.90 | Sec. II.B |
| c_SW | 1.715 (NP, from hep-lat/0508031) | Sec. II.B |
| Lattice | 32³×64 | Sec. II.B |
| a | 0.0907(13) fm (abstract; Sec. II.B writes 0.0907(14)) | abstract |
| a⁻¹ | 2.176(31) GeV (inputs m_π, m_K, m_Ω) | physical-point quark mass table, Sec. IV.B |
| Measurement spacing | every 10 traj (every 20 at κ_ud = 0.13781) | Sec. II.B |

**Ensembles** (κ, τ, MD time: Table "tab:param"; a m_π: Table "tab:hmass"; configs: JLDG page)

| κ_ud | κ_s | τ | MD time | trajectories (derived) | a m_π | m_π (MeV, derived ×2.176) | configs on JLDG |
|---|---|---|---|---|---|---|---|
| 0.13700 | 0.13640 | 0.5 | 2000 | 4000 | 0.32242(65) | 702 | 399 (1 missing) |
| 0.13727 | 0.13640 | 0.5 | 2000 | 4000 | 0.26191(73) | 570 | 400 |
| 0.13754 | 0.13640 | 0.5 | 2250 | 4500 | 0.18903(79) | 411 | 450 |
| 0.13754 | 0.13660 | 0.5 | 2000 | 4000 | 0.17671(129) | 385 | 400 |
| 0.13770 | 0.13640 | 0.25 | 2000 | 8000 | 0.13593(140) | 296 | 800 |
| 0.13781 | 0.13640 | 0.25 | 990 | 3960 | 0.07162(299) | 156 | 198 |

Abstract confirms m_π range "702 MeV down to 156 MeV". JLDG page gives 1.125 GB/config and
DOIs PACS-CS.000001–000006.

**Physical point, arXiv:0911.2561** (Table "tab:param", Sec. II.B–D): same action;
(κ_ud, κ_s) = (0.13778500, 0.13660000), τ = 0.25, 2000 MD units; reweighted to
(0.13779625, 0.13663375); m_π = 135.4(6.2) MeV (Table "tab:hmass_ph"); a = 0.08995(40) fm.
Not among the 6 ensembles on the JLDG PACS-CS page. Config count: unverified (~80 inferred).

**Same action on smaller volumes**

- CP-PACS/JLQCD (arXiv:0704.1937, PRD 78, 011502, Table I): β = 1.90, c_SW = 1.715,
  **20³×40**, κ_ud ∈ {0.13580, 0.13610, 0.13640, 0.13680, 0.13700}, κ_s ∈ {0.13580, 0.13640},
  5000–9200 trajectories. a = 0.0970(26) fm (K input), 0.0936(33) fm ([π,K,φ] input), Table II.
- The **only shared κ pair** is (0.13700, 0.13640): 0807.1661 Sec. II.B and Table "tab:comp":

  | Lattice | a m_π | a m_ρ | a m_N |
  |---|---|---|---|
  | 20³×40 (CP-PACS/JLQCD) | 0.32247(74) | 0.5157(21) | 0.7337(28) |
  | 32³×64 (PACS-CS) | 0.32242(65) | 0.5060(30) | 0.7277(22) |

- The 20³×40 CP-PACS/JLQCD β = 1.90 ensembles (10 ensembles, 500–920 configs, 176 MB/config)
  are public on JLDG (`/gfarm/public/ILDG/JLDG/CP-PACS+JLQCD/RCNF2+1/`). Marsh & Lewis
  (1309.1627) used 790 configs at β = 1.90, 20³×40.
- CP-PACS/JLQCD 16³×32 at β = 1.90 (hep-lat/0309137, hep-lat/0310040 Sec. 5): a⁻¹ = 2.05(5) GeV,
  six κ_ud "in the range 0.1358–0.1370", 3000 traj. Exact κ list unverified; not on JLDG.
- **No 24³×48 ensemble at the PACS-CS κ values was found** in any paper.
- The NP c_SW formula of hep-lat/0508031 (Eq. "Nf3cswformula"):
  c_SW = 1 + 0.113 g0² + 0.0209 g0⁴ + 0.0047 g0⁶ → 1.713 at β = 1.90 (derived), consistent with 1.715.

**m_π L on 24³ at a = 0.0907 fm** (derived, assumes a m_π volume-independent, which
Table "tab:comp" supports at the 0.02% level for m_π, 1–2% shifts for m_ρ, m_N):

| κ_ud | m_π (MeV) | m_π L, 24³ (L = 2.18 fm) | m_π L, 32³ | m_π L, 20³ |
|---|---|---|---|---|
| 0.13700 | 702 | 7.74 | 10.32 | 6.45 |
| 0.13727 | 570 | 6.29 | 8.38 | — (not run) |

**Access (JLDG/ILDG)**

- JLDG front page: "PACS-CS configurations are in public release" (28 Sep 2009).
  Location `/gfarm/public/ILDG/JLDG/PACS-CS/RCNF2+1/`, example LFN
  `lfn://JLDG/PACS-CS/RCNF2+1/RC32x64_B1900Kud01370000Ks01364000C1715-b-002510`
  (https://www.jldg.org/ildg-data/PACSCSconfig.html).
- **Registration is required to download.** "How to download JLDG public configurations"
  (https://www.jldg.org/ILDG-CatSrv/HowToAccess-JLDGConfig.pdf, 17 June 2018): JLDG suspended
  ILDG catalogue services, `ildg-get` does not work; download is via `globus-url-copy` from
  `gsiftp://www2.jldg.org/gfarm/...`; point 8: "using 'Faceted Navigation' requires no
  authentication, while 'grid-proxy-init' with your grid certificate (registered in either
  the ILDG VOMS or the JLDG VOMS) should be completed before downloading any configurations."
- ILDG 2.0 (arXiv:2502.09253, Sec. 3.1–3.3): VOMS replaced by INDIGO IAM (INFN-CNAF),
  membership via eduGAIN identity provider, OAuth2 tokens; "most service providers require
  authentication". Whether JLDG has adopted token/HTTPS access: unverified.
- **No anonymous download route found.** Metadata (Faceted Navigation, QCDml) is anonymous.

---

## 2. Quenched Wilson-plaquette scale and plaquette

**Average plaquette** ⟨P⟩ = ⟨Re Tr U_p⟩/3 = 1 − ⟨S_□⟩, Bali & Schilling hep-lat/9208028 Table 4:

| β | ⟨P⟩ | Lattice / note |
|---|---|---|
| 5.7 | 0.54900(80) | quoted from an earlier compilation |
| 6.0 | 0.593738(17) | 32⁴ |
| 6.2 | 0.613647(8) | 24³×32 |

(Same table: 5.8 → 0.56764(5), 5.9 → 0.58175(6), 6.4 → 0.630647(5); derived as 1 − S.)

**r0/a**

- Necco & Sommer hep-lat/0108008 Eq. (2.6), valid 5.7 ≤ β ≤ 6.92 (0.5%→1% accuracy):
  ln(a/r0) = −1.6804 − 1.7331(β−6) + 0.7849(β−6)² − 0.4428(β−6)³
- Guagnelli, Sommer, Wittig hep-lat/9806005 Eq. (2.18), valid 5.7 ≤ β ≤ 6.57 (0.3%→0.6%):
  ln(a/r0) = −1.6805 − 1.7139(β−6) + 0.8155(β−6)² − 0.6667(β−6)³

| β | r0/a measured | Source | NS (2.6), derived | GSW (2.18), derived |
|---|---|---|---|---|
| 5.7 | 2.922(9) | GSW Table 2 (16³? L/r0 = 3.42) | 2.938 | 2.930 |
| 5.7 | 2.990(24) | Edwards–Heller–Klassen hep-lat/9711003 Table 2 (16³×32) | | |
| 6.0 | 5.369(9) | EHK hep-lat/9711003 Table 2 (16³×32) | 5.368 | 5.368 |
| 6.2 | 7.380(26) | GSW Table 2 | 7.383 | 7.360 |

β = 6.0 was not simulated in GSW/NS. Francis et al. arXiv:1503.05652 give a rational fit
for ln(r0/a) over 5.7–6.92 (c1 = −8.17273, c2 = 14.9600, c3 = −3.95983, c4 = −5.30334).

**Gradient flow** (Wilson flow, Wilson gauge action). No paper tabulates t0/a² at exactly
β = 6.0 or 6.2.

| β | t0/a² | E discretisation | Source |
|---|---|---|---|
| 5.96 | 2.7854(62) | clover | Lüscher 1006.4518 Table 1 (24³×48) |
| 6.17 | 5.489(14) | clover | Lüscher 1006.4518 Table 1 (32³×64) |
| 6.42 | 11.241(23) | clover | Lüscher 1006.4518 Table 1 |
| 5.96 | 2.78867(16) | clover | Cè et al. 1506.06052 Table 3 |
| 6.05 | 3.7825(8) | clover | Cè et al. 1506.06052 Table 3 |
| 6.13 | 4.8722(11) | clover | Cè et al. 1506.06052 Table 3 |
| 6.21 | 6.1957(14) | clover | Cè et al. 1506.06052 Table 3 |
| 6.0625 | 4.0626(41) (clover), 3.7129(39) (plaq.) | | Francis et al. 1503.05652 Table 3 |
| 6.2083 | 6.3284(68) (clover), 5.9521(65) (plaq.) | | Francis et al. 1503.05652 Table 3 |

Continuum: √(8t0)/r0 = 0.941(7), t0 = (0.176(4) fm)² (Cè et al. 1506.06052);
√t0/r0 = 0.3338(28) (Francis et al.). Francis et al. Eq. (7) gives an interpolation of
√t0/a in β. **w0/a** for the quenched Wilson action at β ≤ 6.2: unverified (no tabulation
found; Asakawa et al. 1503.06516 covers only β ≥ 6.3).

---

## 3. NP c_SW, κ_c and quenched NP-clover spectroscopy (M3 gate)

**c_SW** — Lüscher, Sint, Sommer, Weisz, Wolff hep-lat/9609035 Eq. (5.15):

  c_SW = (1 − 0.656 g0² − 0.152 g0⁴ − 0.054 g0⁶) / (1 − 0.922 g0²),  valid 0 ≤ g0 ≤ 1 (β ≥ 6.0), ~3% precision.

Derived: c_SW(6.0) = 1.76923, c_SW(6.2) = 1.61375 (match the 1.769, 1.614 used by QCDSF/UKQCD).
**Not valid at β = 5.7.**

**κ_c** (NP c_SW)

| Source | Definition | β = 6.0 | β = 6.2 |
|---|---|---|---|
| hep-lat/9609035 Table 1 | SF PCAC mass = 0, L/a = 16 | 0.135196(14) | 0.135795(13) |
| hep-lat/9611015 Table 1 | SF, L/a = 8 (12) | 0.135046(16) | 0.135692(6); 0.135705(12) |
| QCDSF hep-lat/9707021 Table 4 | m_π² → 0, phenomenological fit | 0.13531(1) | 0.13589(2) |
| UKQCD hep-lat/9910022 Table XIII | m_π² → 0 | 0.135252(+16/−9) (16³), 0.135235(+9/−10) (32³) | 0.135815(+17/−14) |

**Gate values: QCDSF hep-lat/9707021** (Jacobi smearing). β = 6.0, c_SW = 1.769, Table 2;
MeV with a⁻¹ = 1949 MeV (√K = 427 MeV, a√K = 0.2191(15), Table 8). ~1000 configs (16³)
except heavy κ and 24³ (~200).

| κ | Lattice | a m_π | a m_ρ | a m_N | m_π (MeV, paper) |
|---|---|---|---|---|---|
| 0.1324 | 16³×32 | 0.5039(7) | 0.6157(16) | 0.932(4) | 982 |
| 0.1333 | 16³×32 | 0.4122(8) | 0.5502(23) | 0.821(5) | 803 |
| 0.1342 | 16³×32 | 0.2988(17) | 0.487(3) | 0.705(9) | 582 |
| 0.1342 | 24³×32 | 0.3020(11) | 0.491(3) | 0.686(7) | 589 |
| 0.1346 | 24³×32 | 0.2388(14) | 0.467(6) | 0.626(10) | 465 |
| 0.1348 | 24³×32 | 0.194(4) | 0.448(13) | 0.593(19) | 378 |

β = 6.2, c_SW = 1.614, 24³×48, ~300 configs, Table 3, a⁻¹ = 2652 MeV:

| κ | a m_π | a m_ρ | a m_N | m_π (MeV, paper) |
|---|---|---|---|---|
| 0.1344 | 0.3046(9) | 0.4005(26) | 0.592(9) | 808 |
| 0.1349 | 0.2444(9) | 0.3626(43) | 0.521(13) | 648 |
| 0.1352 | 0.2016(11) | 0.3430(53) | 0.485(6) | 535 |

**Gate values: UKQCD hep-lat/9910022** (degenerate κ; a m_π Table II, a m_V Table III,
a m_N Table VI; MeV derived with r0 = 0.5 fm and GSW r0/a: a⁻¹ = 2120 MeV (6.0), 2907 MeV (6.2)).
Ensembles (Table I): 6.0 16³×48 496 cfg; 6.0 32³×64 70 cfg; 6.2 24³×48 216 cfg.

| β | Lattice | κ | a m_π | a m_V | a m_N | m_π (MeV) |
|---|---|---|---|---|---|---|
| 6.0 | 16³×48 | 0.13344 | 0.3977(+13/−7) | 0.5397(+32/−30) | 0.808(+10/−7) | 843 |
| 6.0 | 16³×48 | 0.13417 | 0.3077(+18/−8) | 0.4852(+53/−53) | 0.711(+16/−13) | 652 |
| 6.0 | 16³×48 | 0.13455 | 0.2493(+22/−12) | 0.4577(+85/−83) | 0.665(+26/−28) | 529 |
| 6.0 | 32³×64 | 0.13344 | 0.3952(+16/−8) | 0.5400(+47/−35) | 0.799(+10/−10) | 838 |
| 6.0 | 32³×64 | 0.13417 | 0.3048(+13/−11) | 0.4887(+61/−48) | 0.700(+11/−15) | 646 |
| 6.0 | 32³×64 | 0.13455 | 0.2457(+14/−10) | 0.4636(+88/−76) | 0.641(+16/−20) | 521 |
| 6.2 | 24³×48 | 0.13460 | 0.2803(+15/−10) | 0.3887(+32/−28) | 0.586(+8/−6) | 815 |
| 6.2 | 24³×48 | 0.13510 | 0.2149(+19/−14) | 0.3531(+55/−51) | 0.509(+10/−10) | 625 |
| 6.2 | 24³×48 | 0.13530 | 0.1836(+23/−18) | 0.3414(+72/−82) | 0.487(+3/−14) | 534 |

Recommended M3 κ (m_π ≈ 500–850 MeV, compare in lattice units to avoid scale ambiguity):
β = 6.0: 0.13344, 0.13417, 0.13455 (UKQCD; 32³×64 is closest in volume to our 24³×48);
β = 6.2: 0.13460, 0.13510, 0.13530. Scale choice (√K vs r0 = 0.5 fm) shifts MeV values by ~9%.

---

## 4. Gluelump spectrum (M2 gate)

**Foster & Michael, hep-lat/9811010** ("Hadrons with a heavy colour-adjoint particle",
PRD 59, 094509 (1999)). Quenched Wilson; β = 5.7 (12³×24, 99 cfg, r0/a = 2.940),
6.0 (16³×48, 202 cfg, 5.272), 6.2 (24³×48, 60 cfg, 7.319) (Table 1). Continuum linear in
(a/r0)²; ~10% quenched scale error on MeV. Table 3 (continuum, relative to T1+−):

| J^PC (irrep) | Δ(M r0) | MeV |
|---|---|---|
| 1−− (T1−−) | 0.933(18) | 368(7) |
| 2−− (T2−−) | 1.438(25) | 584(10) printed; **typo, 567(10)** (Marsh–Lewis Table I footnote; 1.438×394) |
| 2+− (E+−) | 2.467(92) | 973(36) |
| 3+− (A2+−) | 2.468(60) | 972(24) |
| 0++ (A1++) | 2.771(72) | 1092(28) |

Lattice-unit effective masses (Table 2, t = 3:2): T1+− 1.813(15)/1.329(5)/1.142(3),
T1−− 2.006(33)/1.486(4)/1.261(5), T2−− 2.280(45)/1.579(4)/1.331(7) at β = 5.7/6.0/6.2.

**Herr, Schlosser, Wagner, arXiv:2306.09902** (PRD 109, 034516). Pure SU(3) Wilson,
multilevel; β = 6.000, 6.284, 6.451, 6.594 (a = 0.093–0.040 fm); continuum fit from the 3
finest; **r0 = 0.5 fm**. Table 4, ΔM = M − M(1+−) in GeV (errors combined):

| J^PC | ΔM (GeV) | | J^PC | ΔM (GeV) |
|---|---|---|---|---|
| 1−− | **0.342(36)** | | 3+− | 1.376(210) |
| 2−− | 0.523(9)(7)(1) | | 0−− | 1.433(47) |
| 2+− | 0.925(24)(2)(34) | | 3−+ | 1.496(116) |
| 0++ | 0.979(36) | | 2−+ | 1.664(107)(126)(195) |
| 1−+ | 1.213(64) | | 1++ | 1.793(108) |
| 2++ | 1.258(24) | | 0+− | 2.088(138) |
| | | | 3−− | 2.149(340) |
| | | | 3++ | 2.210(95) |
| | | | 0−+ | 2.354(122) |

Per-irrep (Table 3): T1−− 0.342(19)(22)(21), T2−− 0.503(12)(5)(5), E−− 0.559(12)(44)(11).
Some J assignments flagged "plausible but not established". RS mass
Λ_B^RS(ν_f = 2.5/r0) = 0.857(3)(143) GeV (Eq. 41). Sec. 4.2.4: up to ~30% differences from F&M.

**Bali & Pineda, hep-ph/0310130** (quenched, re-uses F&M splittings; r0⁻¹ = 394 MeV):
Λ_B^RS(2.5 r0⁻¹) = [2.25 ± 0.10 ± 0.21 ± 0.08] r0⁻¹ (Eq. 66, from hybrid potentials);
[2.31 ± 0.04 ± 0.33 (+0.18/−0.19)] r0⁻¹ (Eqs. 71, 73, from F&M). Table 4 absolute RS masses:
1+− 2.25(39), 1−− 3.18(41), 2−− 3.69(42), 2+− 4.72(48), 3+− 4.72(45), 0++ 5.02(46),
4−− 5.41(46), 1−+ 5.45(51) (units r0⁻¹). Order (Sec. 2.3): 1+−, 1−−, 2−−, 2+−, 3+−, 0++, 4−−, 1−+.

**Marsh & Lewis, arXiv:1309.1627** ("Lattice QCD study of generalized gluelumps").
**Dynamical** N_f = 2+1 CP-PACS/JLQCD clover (m_π/m_ρ ≈ 0.62–0.64), no continuum limit.
Table IV, GeV: T1−− 0.33±0.02±0.07 (β = 1.90, a = 0.0982 fm, 20³×40, 790 cfg);
0.24±0.05±0.06 (β = 2.05, a = 0.0685 fm, 28³×56, 650 cfg). T2−− 0.67 / 0.64, E+− 0.94 / 1.18.

Schlosser & Wagner 2111.00741: hybrid potentials only, no gluelump spectrum.

**Summary for the M2 gate**

| Source | 1−− − 1+− | in r0 units |
|---|---|---|
| Foster–Michael (quenched, continuum) | 368(7) MeV ± 10% scale | 0.933(18) |
| Herr–Schlosser–Wagner (quenched, continuum, r0 = 0.5 fm) | **0.342(36) GeV** | 0.867(91) (derived) |
| Marsh–Lewis (N_f = 2+1, a = 0.098 / 0.069 fm) | 0.33(2)(7) / 0.24(5)(6) GeV | — |

Ordering agreed by all: **1+− < 1−− < 2−− < 2+− < 0++**; 3+− degenerate with 2+− in F&M
but ~0.45 GeV higher (±0.21) in HSW. Use HSW as primary gate (compare in r0 units).

---

## 5. Static-light (fundamental) spectrum (M3 gate)

S = (1/2)⁻, P₋ = (1/2)⁺, P₊ = (3/2)⁺. Splittings M − M(S) in MeV.

| Source | N_f, setup | P₋ − S | P₊ − S | Location |
|---|---|---|---|---|
| Michael & Peisa hep-lat/9802015 | 0, β = 5.7 tad-clover, 12³×24, κ = 0.14077 | aΔE: 0.339(43) (derived from 1.214(43) − 0.875(6)) | 0.387(56) (derived) | Table 2; P₊−P₋ = 0.068(64) a⁻¹ (text) |
| Green et al. (UKQCD) hep-lat/0312007 | 2, β = 5.2 clover, a ≈ 0.1–0.15 fm, light ≈ m_s | 404(31) (r0ΔE = 1.07(7)) | r0ΔE = 1.33(13) (~500 derived) | text "Lattice spectrum"; Tables 1–2 |
| Koponen hep-lat/0702006 | 2, a = 0.110 fm, light ≈ m_s, HYP static | 430(30) | 420(40) | Table I (v2) |
| BGR, Burch et al. 0809.1103 | 0, LW + CI fermions, continuum, chiral | 435(15)(9) | 423(13)(9) | Table 10 |
| BGR 0809.1103 | 0, continuum, static-strange | 412(10)(8) | 400(8)(8) | Table 11 |
| ETMC Jansen et al. 0810.1843 (JHEP 0812:058) | 2 tm, a = 0.0855 fm, HYP2, phys. u/d | 371(16) | 487(11) | Table 6 |
| ETMC Michael, Shindler, Wagner 1004.4235 | 2 tm, 3 spacings, phys. u/d (B) | **406(19)** | **516(18)** | Table 5 |
| ETMC 1004.4235 | same, B_s | 413(12) | 504(12) | Table 5 |

ETMC 0810.1843 Table 5 per-mass values at a = 0.0855 fm, e.g. m_π = 597 MeV: P₋ 495(16),
P₊ 479(14); m_π = 485 MeV: 456(17), 486(12). 0808.2121 is the Lattice-2008 proceedings
(preliminary, superseded). Ordering: P₋ lighter in ETMC continuum (no inversion at m_s,
1004.4235 Sec. 4); quenched results (Michael–Peisa, BGR) P₋ ≈ P₊ within errors.
Static action used in 1004.4235: unverified.

**M3 gate suggestion:** at heavy valence κ (≈ m_s) compare P₋ − S ≈ 400–450 MeV and
|P₊ − P₋| ≲ 50 MeV (quenched BGR static-strange, Michael–Peisa); with ~20% quenched scale
ambiguity, better to compare r0 ΔE.

---

## 6. R-hadrons: Foster–Michael adjoint mesons, Farrar, Kraan

**Foster & Michael hep-lat/9811010, adjoint mesons** (quenched; flavour non-singlet only, no
disconnected / gluelump mixing; Sec. 4). β = 5.7 tad-clover (8³×16, 12³×24; κ = 0.13843,
0.14077, a m_PS = 0.736, 0.529) and β = 6.0 NP-clover 16³×24 κ = 0.13714 (Table 6 prints
0.13417; a m_PS = 0.309). Channels γ5 (PA), γi (VA), 1 (SA); SA clearly higher (Table 6).
No continuum limit ("not feasible", Sec. 3).

| Quantity | Value | Location |
|---|---|---|
| M_s(PA) − M_s(VA), strange, β = 5.7 | 50(70) MeV | end of Sec. 3 |
| M_s(VA) − G(1+−), strange, β = 5.7 + 6.0 | 120(70) MeV | Sec. 3 |
| VA − G(1+−), chiral, β = 5.7 only | −10(103) MeV | Sec. 3 |
| PA − G(1+−), chiral, β = 5.7 only | 34(161) MeV | Sec. 3 |
| **M(VA) − G(1+−), chiral estimate** | **47(90) MeV** | Sec. 4 |

Sec. 4: one-gluon-exchange colour-spin for an octet q q̄ has −1/8 of the singlet coefficient
→ vector adjoint meson lighter, splitting ~8× smaller. **No R-baryon results** ("We will be
unable to address the issue of the spectrum of 'adjoint baryons'", Sec. 1).

**Farrar and collaborators.** Buccella, Farrar, Pugliese, "R baryon masses", Phys. Lett. B
153, 311 (1985) — bag model, **no arXiv version; original text unverified** (numbers only
via later papers). hep-ph/0702174 is an unrelated paper.

- hep-ph/9407401 Sec. 1: S⁰ (flavour-singlet uds g̃) "probably is the lightest of the
  R-baryons… even lighter than the R-nucleons"; bag estimates "cannot be trusted".
- hep-ph/9603271: S⁰ is "the flavor singlet **scalar** uds g̃", mass "about 210 ± 20 MeV lower
  than that of the lowest R-nucleons" (citing Buccella et al.); 0–1 GeV above R⁰.
- Farrar, Mackeprang, Milstead, Roberts arXiv:1011.2964 Sec. 2: colour-octet qqq has spin
  1/2 or 3/2; J_qqq = 3/2 must be flavour octet; 1/2 can be singlet, octet, decuplet
  (consistent with PLAN §1.3). Table 3 (normalisation m(ñ) = m_g̃ + 660 MeV, from Buccella et
  al.): S⁰ m_g̃ + 280; J = 1 octet m_g̃ + 530; ñ, p̃ (J = 0 octet) m_g̃ + 660; π̃ m_g̃ + 330;
  K̃ m_g̃ + 460 MeV. Meson–baryon offset set by hand. R-meson splittings from Chanowitz–Sharpe
  (Table 1): m_π̃ − m_ρ̃ = 40 MeV (vector lighter). Internal inconsistency: S⁰ − ñ = −380 MeV
  vs −210(20) MeV in hep-ph/9603271.

**Kraan hep-ex/0404001** (EPJ C 37, 91). Colour-magnetic model Eq. (1),
m = Σm_i − k Σ(F_i·F_j)(S_i·S_j)/(m_i m_j), u, d only (m_q = 0.3 GeV), k ≈ 0.043 GeV³ (mesons),
0.026 GeV³ (baryons). C8 q q̄ (Sec. 3.2.1): M_C8 + 0.66 GeV (s = 0), + 0.58 GeV (s = 1):
vector ~80 MeV below pseudoscalar ("hierarchy is reversed"). C8 qqq splittings not computed
("not more than the order of a hundred MeV"). Gluino-ball: gluon constituent ~0.7 GeV.
**No strange quarks, so no S⁰; no table of masses vs m_g̃.**

---

## 7. Static actions (ALPHA) and HYP

Della Morte, Shindler, Sommer hep-lat/0506008 (JHEP 0508:051), Sec. 2:
S_h^W = a⁴ (1 + aδm_W)⁻¹ Σ ψ̄_h (D₀^W + δm_W) ψ_h, D₀^W ψ_h(x) = [ψ_h(x) − W†(x−a0̂,0) ψ_h(x−a0̂)]/a.

| Action | W(x,0) | Unitary? | r⁽¹⁾ (one loop) | aE_stat (β = 6) | aV(0) |
|---|---|---|---|---|---|
| EH | U(x,0) | yes | 0.16845(2) | 0.68(9) | 0 |
| A ("APE") | V(x,0) = average of 6 staples, **no projection** | no | 0.05737(4) | 0.85(2) | 0.671(2) |
| s | V [g0²/5 + ((1/3)tr V†V)^{1/2}]⁻¹ (approx. one-link integral; not stout) | no | 0.05737(4) | 0.76(2) | 0.496(2) |
| HYP1 | HYP link, α = (0.75, 0.6, 0.3) | yes | 0.04844(1) | 0.44(2) | 0 |
| HYP2 | HYP link, α = (1.0, 1.0, 0.5) | yes | 0.03523(1) | 0.41(1) | 0.00001(1) |

(Table 1 of hep-lat/0506008.) HYP2 from approximate minimisation of R_NS; HYP1 from
Hasenfratz–Knechtli hep-lat/0103029 (α = 0.75, 0.6, 0.3, maximising smallest plaquette;
intermediate SU(3) projection "very important"). ALPHA defines the SU(3) projection by a fixed
analytic iteration (normalise, then 4 iterations of X = W(3/2 − W†W/2),
W → X(1 − (i/3) Im det X)). Self-energy E_self ~ e⁽¹⁾g0²/a; for non-unitary W the relevant
quantity is E_self − V(0)/2 ~ r⁽¹⁾g0²/a.

Noise/signal (Sec. 2.1): R_NS ∝ exp{[E_stat − (m_π + V(0))/2] x0}; HYP2 best, signal to ~2 fm
(16³×32, β = 6, κ = 0.133929, ~5000 cfg). hep-lat/0307021 (PLB 581, 93): R_NS ∝ exp(x0 Δ),
Δ = E_stat − m_π (EH); Δ reduced by ~4 with new actions; uses HYP1 only. Erratum content: unverified.

---

## 8. ATLAS R-hadron model: ATL-PHYS-PUB-2019-019 (CDS 2676309)

"Generation and Simulation of R-Hadrons in the ATLAS Experiment", 21 May 2019. Read from the
identical file on INSPIRE (record 1747315; CDS blocked automated access). Page numbers refer
to that 19-page PDF.

**Table 1 (p. 5): constituent quark masses (GeV), 10 sets.** No gluon or gluino column.

| Set | u = d | s | c | b |
|---|---|---|---|---|
| Pythia6 [52] (Mackeprang thesis 2007) | 0.325 | 0.50 | 1.60 | 5.00 |
| Meson fits [53] | 0.314 | 0.466 | 1.63 | – |
| Baryon fits [53] (**ATLAS default**) | 0.365 | 0.53 | 1.7 | – |
| Relativised quark model [54] | 0.220 | 0.419 | 1.628 | 4.977 |
| Feynman–Hellmann best fit [55] | 0.3 | 0.475 | 1.640 | 4.990 |
| Meson fits [56] | 0.310 | 0.483 | 1.7 | – |
| Meson spectroscopy [57] | 0.290 | 0.460 | 1.65 | 4.80 |
| Light/strange hadron fits [58] | 0.360 | 0.540 | 1.71 | 5.50 |
| Goldberger–Treiman [59] | 0.3375 | 0.486 | 1.550 | 4.73 |
| Hadron fits [60] | 0.311 | 0.487 | 1.592 | – |

**Table 2 (p. 6): offsets relative to the constituent gluino mass (GeV)**, light states.
Columns: Pythia6 | meson fit | baryon fit (default) | min | max (min/max are per-hadron
extremes over the 10 sets).

| PDG ID | State | Content | Pythia6 | Meson fit | **Default** | Min | Max |
|---|---|---|---|---|---|---|---|
| 1000993 | gluinoball | g̃g | 0.700 | 0.700 | 0.700 | 0.700 | 0.700 |
| 1009113 / 1009223 / 1009213 | ρ⁰ / ω / ρ⁺ | g̃qq̄ | 0.650 | 0.610 | 0.717 | 0.403 | 0.717 |
| 1009313 / 1009323 | K*⁰ / K*⁺ | g̃sq̄ | 0.825 | 0.768 | 0.886 | 0.620 | 0.891 |
| 1009333 | φ | g̃ss̄ | 1.800 | 0.924 | 1.054 | 0.828 | 1.074 |
| 1093214 | Λ⁰ | g̃uds | 1.150 | 0.562 | 0.715 | 0.280 | 0.715 |
| 1091114 / 1092114 / 1092214 / 1092224 | Δ⁻,⁰,⁺,⁺⁺ | g̃qqq | 0.975 | 0.812 | 0.965 | 0.530 | 0.965 |
| 1093114 / 1093224 | Σ*⁻ / Σ*⁺ | g̃sqq | 1.150 | 1.094 | 1.260 | 0.859 | 1.260 |
| 1093314 / 1093324 | Ξ*⁻ / Ξ*⁰ | g̃ssq | 1.300 | 1.246 | 1.425 | 1.058 | 1.440 |
| 1093334 | Ω⁻ | g̃sss | 1.600 | 1.398 | 1.590 | 1.257 | 1.620 |

Heavy-flavour rows (J/ψ, Υ, D*, B*, Σ_c*, …) are also in Table 2; not transcribed here.

**Model (pp. 3–5).**
- Gluinoball: constituent gluon mass 700 MeV, m = m_g̃ + 0.700 GeV, fixed in every column. Varied
  only indirectly by two modified spectra shifting all quark states by ±107 MeV (p. 5).
- R-mesons, J = 1 only (Eq. 3): offset = m_q + m_q̄ − k (1/24)/(m_q m_q̄), k ≈ 0.043 GeV³
  (reproduces 0.610, 0.717, 0.403). **There is a colour-magnetic hyperfine term**; J = 0
  R-mesons (R-π, PDG 1009111/1009211) are simply not included because Pythia8 keeps only J = 1.
- Lightest R-baryons from bag-model splittings (ref. [24], Buccella–Farrar–Pugliese):
  R-Δ = 3m_u − 0.130, R-Λ = 3m_u − 0.380 GeV (reproduces all columns; the m_s independence of
  R-Λ is our inference from the numbers). Other baryons: plain constituent sums.
- Pythia8 default (not ATLAS) is a sum of constituent masses plus a 200 MeV gluon-cloud offset.
- Gluinoball formation fraction: Pythia8 default 10%, varied.

**Same-set differences (recomputed over all 10 sets of Table 1):**

| Difference | Range (10 sets) | Pythia6 column |
|---|---|---|
| Λ(g̃g) − Λ(g̃qq̄) | −0.017 (baryon fit) to +0.297 ([54]) GeV | +0.050 |
| Λ(g̃uds) − Λ(g̃qq̄) | −0.123 ([54]) to −0.002 (baryon fit) GeV | +0.500 |
| Λ(g̃sq̄) − Λ(g̃qq̄) | +0.153 ([59]) to +0.217 ([54]) GeV | +0.175 |

---

## 9. N_f = 3+1 gluelumps: arXiv:2501.15670

Höllwieser, Knechtli, Korzec, Peardon, Struckmeier, Urrea-Niño, "Hybrid static potentials and
gluelumps on N_f=3+1 ensembles", LATTICE2024 proceedings (PoS volume number unverified).

| Ensemble | Flavours | Volume | β | m_π | r0/a | a (fm) | N_cfg |
|---|---|---|---|---|---|---|---|
| qE | quenched (plaquette) | 48×24³ | 5.85 | – | 4.2612(42) | 0.0662(12) | 6480 |
| Em1 | N_f = 2 at m_c/2 (plaquette) | 48×24³ | 5.3 | 2.2(1) GeV | 4.2866(24) | 0.0658(10) | 7098 |
| A1h | 3+1, LW + NP clover | 96×32³ | 3.24 | 788(6) MeV | 7.278(27) | 0.0690(11) | 4000 |
| A1 | 3+1 | 96×32³ | 3.24 | 406(3) MeV | 9.023(63) | 0.05359(15) | 4000 |
| A2 | 3+1 | 128×48³ | 3.24 | 409(1) MeV | 8.998(54) | 0.05355(13) | 2000 |

(Table 1; a from the h_c–η_c splitting; open temporal boundaries for 3+1; HYP2 static links,
3 APE levels, 35 loop shapes; Γ-method via pyerrors.)

- **No table of gluelump masses.** Spectrum only in Fig. 1 as r0(am_Λ − am_T1+−), no MeV, no
  continuum limit. 1+− is lowest; plotted order follows Foster–Michael (1+−, 1−−, 2−−, 2+−,
  0++, 3+−, …). Text: splittings "consistently increas[e] with decreasing pion mass".
- Read off Fig. 1 by eye (not numbers in the paper; treat as ±0.1): r0Δ(1−−) ≈ 0.45 (qE),
  0.65 (Em1), 0.8 (A1h, A1); r0Δ(2−−) ≈ 0.9, 1.3, 1.55, 1.8. The qE value is well below
  HSW's continuum 0.87/r0 and F&M's 0.93/r0; r0 = (r0/a)·a comes out at ~0.28 fm for qE/Em1
  vs ~0.48–0.50 fm for the 3+1 ensembles (derived), so cross-ensemble comparison in r0 units
  is suspect. **Not usable as a quantitative gate.**
- Thresholds discussed are only **fundamental** static-light ones for hybrid-potential string
  breaking (2m_S, m_S + m_P1/2, …; Fig. 2). **No adjoint static + light-quark (R-meson) states
  and no gluelump → R-meson threshold** are computed. Static-light correlators listed as future work.

---

## 10. Search for unquenched R-meson / R-baryon lattice computations

**Result: one preliminary unquenched R-meson computation exists; no R-baryon computation
(quenched or unquenched) was found.**

| arXiv | What | Dynamical? | Relevance |
|---|---|---|---|
| **2603.29581** (PoS LATTICE2025 086) Sharma, Urrea-Niño, Brambilla, Knechtli, Peardon, "Imprint of the adjoint meson spectrum in the decay patterns of hidden-bottom tetraquarks" | q̄ΓT^a q + adjoint static line (I = 1), channels 0⁻⁺, 1⁻⁻, 1⁺⁺, 0⁺⁻, 0⁺⁺, 1⁺⁻; distillation (100 vectors) | **N_f = 3+1**, 32³×96, a ≈ 0.052 fm, m_π ≈ 406 MeV, 4000 cfg | Effective masses only, no plateaus, **no masses quoted**; 0⁻⁺ and 1⁻⁻ "good indications" of degeneracy; GEVP pending |
| hep-lat/9811010 Foster & Michael | adjoint mesons + gluelumps | quenched | only full quenched R-meson study (§6) |
| hep-lat/9709051 Foster & Michael | gluelumps only | quenched | lowest splitting 354±9 MeV (abstract) |
| 1309.1627 Marsh & Lewis | generalized gluelumps, no valence quarks | 2+1 sea | gluelumps only |
| 2501.15670 | gluelumps, hybrids | 3+1 sea | gluelumps only (§9) |
| 2408.04719 (BOEFT review) | states gluelump vs adjoint-meson ordering unclear; dynamical lattice "indispensable" | – | context |
| 2610.06009 Alasiri, Braaten, Bruschini (Sec. 3.4) | "Adjoint baryons": only lattice colour-octet results are gluelumps; adjoint-baryon splittings "no such information is yet available" | – | confirms no R-baryon lattice result |
| hep-lat/0001020, 9902003, 9912050, 9902002 | adjoint string breaking (into gluelumps) | quenched / pure gauge | no light-quark adjoint mesons |
| 1206.2341, 1512.07014, 1801.08062, 1902.11127 | SYM gluino-glue | dynamical adjoint Majorana gluino | different physics (no static source, no quarks) |

Searches run: 9 WebSearch queries (R-hadron/adjoint static + light quarks, gluino lattice
spectrum, adjoint meson + Knechtli/Urrea-Niño, adjoint string breaking dynamical, adjoint
baryon/gluino baryon, octet static-light, SYM gluino-glue, …); INSPIRE API: citations of
hep-lat/9811010 (recid 478948, 163 citations, ~100 arXiv records scanned; near-complete),
`t gluelump` (9), `t "R-hadron" and t lattice` (0), `t adjoint and t "string breaking"` (6),
`t "adjoint meson(s)" or t R-meson or t R-baryon or t R-hadrons` (23), references of 2610.06009.

---

## Corrections to PLAN.md

1. **§3 Stage B, PACS-CS statistics.** Not "~400 cfgs each": 399 / 400 / 450 / 800 configs at
   m_π = 702 / 570 / 411 / 296 MeV (plus 400 at 385 MeV with κ_s = 0.13660, 198 at 156 MeV).
   a = 0.0907(13) fm, a⁻¹ = 2.176(31) GeV; κ_s = 0.13640 for the main series. β = 1.90,
   c_SW = 1.715, 32³×64 confirmed (0807.1661 Sec. II, Tables tab:param, tab:hmass; JLDG page).
2. **§3/§8 "public via JLDG/ILDG".** Publicly released, but **download requires a grid
   certificate registered in the ILDG or JLDG VO** (`globus-url-copy`; `ildg-get` no longer
   works for JLDG). No anonymous route. (JLDG HowToAccess PDF, 2018, point 8; ILDG 2.0:
   2502.09253.) The user must register or choose "self-generate".
3. **§3 Stage B fallback.** No published 24³×48 run at PACS-CS κ exists. m_π L on 24³ is
   7.74 (702 MeV) and 6.29 (570 MeV) — fine. Cheaper alternative for the 702 MeV point:
   CP-PACS/JLQCD 20³×40 at identical (0.13700, 0.13640), β = 1.90, c_SW = 1.715, public on
   JLDG (same registration), a m_π = 0.32247(74), m_π L = 6.45 (0807.1661 Table tab:comp;
   0704.1937 Table I).
4. **§2 static action / §6 "HYP2 vs HYP1/APE".** HYP1 = (0.75, 0.6, 0.3), HYP2 = (1.0, 1.0, 0.5)
   confirmed (hep-lat/0506008 Sec. 2.2). The ALPHA "APE" (A) and "s" static links are
   **non-unitary** (aV(0) = 0.671, 0.496): the adjoint construction
   U_adj = 2Tr[T^a W T^b W†] is then not in SO(8) and the §6 unit test fails. **Use HYP1 as the
   second static action** (or an SU(3)-projected APE link, which is a different action from
   ALPHA's A).
5. **§2 "adjoint noise ~9/4 worse in the exponent".** Not stated in any verified source.
   9/4 = C_A/C_F is the one-loop ratio of the self-energy; the noise exponent per
   hep-lat/0506008 is E_stat − (lightest state in the squared correlator)/2, which for the
   adjoint is not simply 9/4 × fundamental. Mark as an estimate (unverified).
6. **§1.4 item 2 (Foster & Michael).** Refine: chiral estimate M(VA) − G(1+−) = 47(90) MeV;
   strange-quark VA − G = 120(70) MeV; PA − VA (strange) = 50(70) MeV (hep-lat/9811010 Secs. 3–4).
   "Within ~100 MeV" reflects 70–160 MeV errors more than central values. Quenched, flavour
   non-singlet only, κ near m_s or heavier, chiral extrapolation from β = 5.7 only, no continuum
   limit, **no R-baryons**. Paper submitted Nov 1998, published PRD 59, 094509 (1999). The
   −1/8 colour-spin argument (vector lighter) is explicit in Sec. 4; Kraan's model and
   Chanowitz–Sharpe (via 1011.2964) also put the vector lower.
7. **§1.3 "Farrar's candidate lightest R-baryon".** Farrar's S⁰ is the **J = 0** (scalar)
   uds g̃ — the J = 0 member of our j_light = ½ flavour-singlet doublet (hep-ph/9603271;
   1011.2964 Sec. 2). Bag-model estimate S⁰ ≈ 210(20) MeV below the lowest R-nucleon
   (hep-ph/9603271) or 250/380 MeV below the J = 1/J = 0 octets (1011.2964 Table 3).
   SU(6) content (8,½),(8,3/2),(10,½),(1,½) confirmed by 1011.2964 Sec. 2.
8. **§5 M0 citation list.** "Buccella–Farrar–Pugliese" = Phys. Lett. B 153, 311 (1985), no arXiv
   ID (hep-ph/0702174 is unrelated). Relevant Farrar arXiv papers: hep-ph/9407401,
   hep-ph/9603271, hep-ph/9504295, hep-ph/9704310, 1011.2964. Kraan hep-ex/0404001 has **no
   strange quarks / no S⁰** and no mass table vs m_g̃ — usable only for the q q̄ hyperfine sign.
9. **§5 M0 citation list (Marsh–Lewis).** 1309.1627 is **N_f = 2+1 dynamical** (CP-PACS/JLQCD),
   not quenched, no continuum limit — not a quenched M2 reference; use for Stage B comparison.
10. **§5 M2 gate.** Use Herr–Schlosser–Wagner (2306.09902, PRD 109, 034516) Table 4:
    1−− − 1+− = 0.342(36) GeV at r0 = 0.5 fm [0.867(91)/r0, derived]; F&M 0.933(18)/r0.
    Compare in r0 units. Ordering 1+− < 1−− < 2−− < 2+− < 0++. Note F&M's 2−− "584 MeV" is a
    typo for 567(10) MeV. F&M's 3+− ≈ 2+− degeneracy is not confirmed by HSW.
11. **§5 M3 gate.** Use QCDSF hep-lat/9707021 Tables 2–3 and UKQCD hep-lat/9910022
    Tables I–III, VI (§3 here); concrete κ at β = 6.0: 0.13344, 0.13417, 0.13455
    (m_π ≈ 840, 650, 525 MeV). The plan's "3 κ from m_s to ~m_s/3" should be fixed to these
    published κ so results compare directly. ALPHA c_SW formula valid only for β ≥ 6.0
    (hep-lat/9609035 Eq. 5.15): c_SW = 1.769 (6.0), 1.614 (6.2). κ_c(6.0) ≈ 0.1352–0.1354
    (spectroscopic) vs 0.135196(14) (SF).
12. **§5 M3 static-light reference.** Quenched results give P₋ ≈ P₊ within errors (BGR
    continuum 435(15)(9) vs 423(13)(9) MeV); N_f = 2 continuum ETMC gives P₋ lighter,
    406(19) vs 516(18) MeV (1004.4235 Table 5). "ETMC 0808.2121" is the Lattice-2008
    proceedings; the JHEP paper is 0810.1843.
13. **§2 scale / §6 regression.** No t0/a² or w0/a tabulated at exactly β = 6.0/6.2 for the
    quenched Wilson action: use Cè et al. 1506.06052 (β = 5.96–6.21) or the Francis et al.
    interpolation (1503.05652 Eq. 7). r0/a: 2.922(9) (5.7), 5.368 from NS Eq. (2.6) or
    5.369(9) measured (6.0), 7.380(26) (6.2). Plaquette: 0.54900(80), 0.593738(17),
    0.613647(8) (hep-lat/9208028 Table 4). Stage A volumes check out: L = 2.05, 2.24, 2.17 fm
    for 12³, 24³, 32³ at β = 5.7, 6.0, 6.2 (derived, r0 = 0.5 fm).
14. **§1.5 Table 2 values are the Pythia6 column, not the ATLAS default.** Default (baryon-fit
    set, Table 1 [53]) offsets: R-ρ 0.717, R-K* 0.886, R-φ 1.054, R-Λ⁰ 0.715, gluinoball 0.700 GeV.
    The 1.800 (φ) and 1.150 (Λ⁰) entries are transcribed correctly but are the old Pythia6
    spectrum, which is why they lie outside min–max. Relabel the column "Pythia6" and add the
    default column (ATL-PHYS-PUB-2019-019 Table 2, p. 6; "baryon fit constituent masses are taken
    as the default", p. 5).
15. **§1.5 "no hyperfine structure" is wrong.** Eq. 3 has a colour-magnetic term for J = 1
    R-mesons (k ≈ 0.043 GeV³), and R-Λ/R-Δ use bag-model hyperfine splittings (−0.380/−0.130 GeV
    from 3m_u). Correct statement: only J = 1 R-mesons are included, so no R-π vs R-ρ
    distinction; no R-nucleon (J_qqq = ½ octet) states tabulated; no excitations.
16. **§1.5 "spread over ten published sets".** 10 sets, yes, and min/max reproduce exactly,
    but min/max are per-hadron extremes (not one set), one set is a thesis, and the note's
    systematic also includes the ±107 MeV shifted spectra and the gluinoball fraction.
17. **§1.5 same-set differences.** [−0.017, +0.297], [−0.12, 0.00] and +0.50 (Pythia6) hold;
    Λ(g̃sq̄) − Λ(g̃qq̄) is [+0.153, +0.217] GeV over all ten sets ([+0.16, +0.22] holds only over
    the five Table 2 columns).
18. **§1.5 "2025 N_f=3+1 gluelump study … with string-breaking thresholds".** 2501.15670 is a
    LATTICE2024 proceedings with gluelump splittings only as a figure (r0 units, no MeV, no
    continuum); its thresholds are fundamental static-light (hybrid potentials), not
    gluelump → R-meson. Not a quantitative reference.
19. **§1.5 "No unquenched lattice computation of R-mesons or R-baryons is known".** Update:
    arXiv:2603.29581 (LATTICE2025, N_f = 3+1, m_π ≈ 406 MeV, a ≈ 0.052 fm) computed I = 1 adjoint
    meson correlators — preliminary, no masses extracted. Same group (Knechtli, Peardon,
    Urrea-Niño et al.) is active; a full paper may appear. No R-baryon lattice computation
    found (confirmed by 2610.06009 Sec. 3.4). Foster–Michael remain the only R-meson numbers.
