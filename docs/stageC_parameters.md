# Stage C: second (finer) lattice spacing, Iwasaki + NP clover, N_f = 2+1

Compiled 2026-11-26. Every number marked **[V]** was read from the full text (PDF) of the arXiv paper
named next to it. **[D]** marks a value I derived myself; it is not in any source. **[U]** marks an
unverified value.

Our current setup (reference point): PACS-CS, beta = 1.90, c_SW = 1.715, 32^3 x 64,
a = 0.0907(13) fm, kappa_s = 0.13640 (one run at 0.13660), kappa_ud = 0.13700, 0.13727, 0.13754,
0.13770, 0.13781, m_pi = 702 -> 156 MeV **[V]** arXiv:0807.1661, abstract and Table I.
The physical-point reweighted value at the same beta is a = 0.08995(40) fm, with
(kappa_ud, kappa_s) = (0.13779625, 0.13663375) **[V]** arXiv:0911.2561, text and Fig. 1/2 captions.

---

## 1. CP-PACS/JLQCD N_f = 2+1 ensembles (same action as ours)

Sources:
- arXiv:0704.1937 (Ishikawa et al., PRD 78, 011502 (2008)), Table I (parameters) and Table II (spacings).
- arXiv:hep-lat/0610050 (PoS LAT2006:181), Table 1.

Action: Iwasaki gauge action plus clover quarks, with c_SW the NP value from hep-lat/0508031. Volume is
about (2.0 fm)^3. There are 5 kappa_ud x 2 kappa_s = 10 points per beta. The configurations are public
on ILDG/JLDG **[V]** arXiv:1202.4719, Sec. II.

| beta | L^3 x T | c_SW | a [fm] K-input (0704.1937 T.II) | a [fm] phi-input | a [fm] (pi,K,phi) | a [fm] K-input (0610050 T.1) |
|---|---|---|---|---|---|---|
| 1.83 | 16^3 x 32 | 1.761 | 0.1174(23) | 0.1184(26) | 0.1095(25) | 0.1222(17) |
| 1.90 | 20^3 x 40 | 1.715 | 0.0970(26) | 0.0971(25) | 0.0936(33) | 0.0994(19) |
| **2.05** | **28^3 x 56** | **1.628** | **0.0701(29)** | 0.0702(28) | 0.0684(41) | 0.0693(26) |

All entries are **[V]**. The PRD (0704.1937) values are the final ones. The LAT2006 values are preliminary.

### kappa values and m_PS/m_V **[V]** (0704.1937, Table I)

beta = 2.05, 28^3 x 56, c_SW = 1.628:

| kappa_ud | kappa_s = 0.13510: m_PS/m_V (LL) | (SS) | kappa_s = 0.13540: m_PS/m_V (LL) | (SS) | traj. |
|---|---|---|---|---|---|
| 0.13470 | 0.7757(26) | 0.7273(29) | 0.7790(23) | 0.6821(32) | 6000 |
| 0.13510 | 0.7316(24) | 0.7316(24) | 0.7341(29) | 0.6820(39) | 6000 |
| 0.13540 | 0.6874(30) | 0.7395(23) | 0.6899(34) | 0.6899(34) | 6000 |
| 0.13550 | 0.6611(34) | 0.7361(25) | 0.6679(45) | 0.6899(43) | 6500 |
| 0.13560 | 0.6337(38) | 0.7377(28) | 0.6361(47) | 0.6852(46) | 6500 |

The MD step at beta = 2.05 is delta tau = 1/175 to 1/250, with N_poly = 200 (kappa_s = 0.13510) and
250 (kappa_s = 0.13540).

beta = 1.90, 20^3 x 40, c_SW = 1.715. kappa_s is 0.13580 or 0.13640. kappa_ud is 0.13580, 0.13610,
0.13640, 0.13680, 0.13700, with m_PS/m_V (LL) from 0.767 down to 0.624.

beta = 1.83, 16^3 x 32, c_SW = 1.761. kappa_s is 0.13710 or 0.13760. kappa_ud is 0.13655, 0.13710,
0.13760, 0.13800, 0.13825, with m_PS/m_V (LL) from 0.777 down to 0.608.

**Pion masses.** The paper gives only m_PS/m_V per ensemble. It states that "the lightest pion mass
in this simulation" is about 620 MeV **[V]** (0704.1937, text near Table II). It does not say which
beta that refers to. Absolute m_pi values per beta = 2.05 ensemble are **[U]**. WHOT-QCD uses the point
(beta, kappa_ud, kappa_s) = (2.05, 0.1356, 0.1351), with m_pi/m_rho about 0.63,
m_eta_ss/m_phi about 0.74, r0/a = 7.06(3), and 1/a about 2.79 GeV from r0 = 0.5 fm **[V]**
(arXiv:1202.4719, Sec. II; arXiv:1710.10015, Sec. 3).

**Scale-setting consistency.** Our a = 0.0907 fm at beta = 1.90 is the PACS-CS value, from a
near-physical-point analysis with m_pi, m_K, m_Omega input. CP-PACS/JLQCD gets 0.0970 fm at the same
beta from heavy-pion chiral extrapolations with rho input. Treat the CP-PACS/JLQCD number at
beta = 2.05 as indicative only. The spacing at our own beta = 2.05 ensembles must be set with the same
scheme we use at beta = 1.90 (for example w0/t0 or m_Omega).

---

## 2. Later work at a finer spacing

| Group / paper | beta | Fermion action | c_SW | a [fm] | Lattice | Same action as ours? |
|---|---|---|---|---|---|---|
| WHOT-QCD, arXiv:1202.4719 / 1112.2756 | 2.05 | NP clover, no smearing | 1.628 (from 0508031) | ~0.07 (r0) | 28^3x56 (T=0, CP-PACS/JLQCD); 32^3 x N_t (finite T) | **Yes.** Reuses the CP-PACS/JLQCD T=0 ensemble. No new T=0 ensembles. **[V]** |
| PACS-CS, arXiv:1006.1164 (SF renormalization) | 1.83, 1.90, 2.05 (+ weak coupling) | NP clover, no smearing | NP | (SF boxes only) | small SF boxes | Yes. Gives Z-factors at beta = 2.05 (Tables VII, X). No large-volume ensembles. **[V]** |
| PACS (PACS10), arXiv:2311.10345 Table I; arXiv:2505.10998 Table 3 | 2.00 | **6-step stout-smeared** clover, rho = 0.1 | 1.02 (NP, SF; Taniguchi arXiv:1303.0104) | 0.06343(14) [2311.10345]; 0.06333(14) [2505.10998] | 160^4 | **No.** Different fermion action. **[V]** |
| PACS (PACS10/PACS5), arXiv:2505.10998 Table 3 | 1.82 | 6-step stout clover, rho = 0.1 | 1.11 | 0.08520(16) | 128^4, 64^4 | **No.** Different action. **[V]** |

PACS10 beta = 2.00 runs at (kappa_ud, kappa_s) = (0.125814, 0.124925), m_pi = 138 MeV. PACS10 beta = 1.82
runs at (0.126177, 0.124902) **[V]**. These kappa values belong to the stout action. They cannot be
used with unsmeared clover, and the stout-clover beta = 2.00 spacing cannot be combined with our
beta = 1.90 point in one O(a^2) extrapolation.

I found no other N_f = 2+1 Iwasaki + unsmeared NP-clover zero-temperature ensembles finer than
beta = 2.05 (searched arXiv/INSPIRE through web search). Treat this as **[U]**; a negative result from
web search is not conclusive.

---

## 3. NP c_SW for the Iwasaki action, N_f = 3 (arXiv:hep-lat/0508031)

Eq. (45), with g0^2 = 6/beta **[V]**:

    c_SW(g0^2, L*) = 1 + 0.113 g0^2 + 0.0209(72) g0^4 + 0.0047(27) g0^6      (chi^2/dof = 0.58)

The companion formula for the SF critical hopping parameter, Eq. (46) **[V]**:

    kappa_c = 1/8 + 0.003681192 g0^2 + 0.000211(43) g0^4 + 0.000067(66) g0^6 - 0.000038(21) g0^8

- c_SW is defined at a fixed physical box L* (T* = 2L*). L*/a = 6 at beta = 1.9, and L*/a at other beta
  follows from the two-loop beta function (Sec. III B, Table II) **[V]**.
- **Range.** The fit uses only data where the perturbative finite-L correction is below 5%. These are
  beta = 12.0, 8.85, 2.2, 2.1, 2.0, 1.9 (Sec. IV C) **[V]**. The lowest simulated beta for N_f = 3 is
  1.90 (Table XI). The formula is therefore an interpolation for 1.9 <= beta <= 12 (and joins
  perturbation theory above). beta = 1.83 is a mild extrapolation.
- Direct NP values at L*, from Table XI **[V]**: beta = 1.90: 1.739(53); 2.00: 1.650(51); 2.10: 1.633(58);
  2.20: 1.542(29).
- The formula reproduces the c_SW values the collaborations used **[D]**:

| beta | g0^2 | c_SW, Eq. (45) [D] | c_SW used in simulations [V] | kappa_c (SF), Eq. (46) [D] |
|---|---|---|---|---|
| 1.83 | 3.2787 | 1.7608 | 1.761 (0704.1937) | 0.13731 |
| 1.90 | 3.1579 | 1.7133 | 1.715 (0704.1937, 0807.1661) | 0.13706 |
| 1.95 | 3.0769 | 1.6825 | n/a | 0.13687 |
| 2.00 | 3.0000 | 1.6540 | n/a | 0.13667 |
| **2.05** | 2.9268 | **1.6276** | **1.628** (0704.1937) | 0.13647 |
| 2.10 | 2.8571 | 1.6031 | n/a | 0.13627 |
| 2.20 | 2.7273 | 1.5590 | n/a | 0.13587 |

The SF kappa_c does not give the dynamical kappa_c. CP-PACS/JLQCD report negative VWI ud masses at
their simulation points (hep-lat/0610050, footnote 1). Our kappa values must therefore be tuned with
runs of our own, not taken from Eq. (46).

---

## 4. Lattice-size estimates for L of about 2.2 fm **[D]**

beta = 2.00 and 2.10/2.20 have no measured N_f = 2+1 spacing. For those, a is interpolated or
extrapolated with ln a linear in beta through the CP-PACS/JLQCD K-input points 0.0970 fm (beta = 1.90)
and 0.0701 fm (beta = 2.05). That slope is -2.165 per unit beta. All entries in this table are **[D]**.
On the PACS-CS scale the spacings are probably about 5-7% smaller (0.0907/0.0970 = 0.935).

| Setup | a [fm] | L/a for 2.2 fm | L at 32^3 [fm] | Fits <= 32^3x64? | a^2 / a^2(1.90) |
|---|---|---|---|---|---|
| beta = 2.00, unsmeared NP clover, c_SW = 1.654 | ~0.078 (interp.) | ~28 | ~2.5 | Yes (28^3x56 or 32^3x64) | ~0.65 |
| **beta = 2.05, unsmeared NP clover, c_SW = 1.628** | **0.0701 (measured)** | **31.4** | **2.24** | **Yes, 32^3x64** | **0.52** |
| beta = 2.10, unsmeared NP clover, c_SW = 1.603 | ~0.063 (extrap.) | ~35 | ~2.0 | Only with L of about 2.0 fm | ~0.42 |
| beta = 2.20, unsmeared NP clover, c_SW = 1.559 | ~0.051 (extrap.) | ~43 | ~1.6 | No | ~0.27 |
| PACS stout clover, beta = 2.00, c_SW = 1.02 | 0.0634 (measured, but a different action) | ~35 | 2.03 | Marginal; also the wrong action | n/a |

Finite-volume constraint: m_pi L >= 4 at L = 2.24 fm means m_pi >= ~350 MeV **[D]**. At beta = 2.05 on
32^3, the PACS-CS-like light points (m_pi below 300 MeV) would therefore have sizeable finite-volume
effects. Plan the continuum extrapolation at matched, heavier pion masses (roughly 400-700 MeV) on both
spacings.

---

## Recommendation

Use **beta = 2.05, c_SW = 1.628, 32^3 x 64**. This is the CP-PACS/JLQCD fine point, with the same
Iwasaki + unsmeared NP-clover action as our beta = 1.90 PACS-CS runs.
- a is about 0.070 fm, measured (0704.1937 Table II). With 32^3 the box is L of about 2.24 fm. a^2 is
  about half its value at beta = 1.90, which gives a good lever arm. c_SW comes straight from the
  hep-lat/0508031 formula, inside its fitted range.
- Starting kappa values **[V]** (0704.1937 Table I): kappa_s = 0.13510 or 0.13540 (strange near
  physical, m_etass/m_phi about 0.74 at 0.13510). kappa_ud = 0.13470, 0.13510, 0.13540, 0.13550,
  0.13560, giving m_PS/m_V = 0.78 down to 0.63. Lighter pions need kappa_ud above 0.13560, to be tuned
  with short runs of our own **[D]**.
- Option: thermalize from or cross-check against the public CP-PACS/JLQCD 28^3 x 56 configurations
  (ILDG/JLDG).
- Set the scale at both betas with one common quantity, and match pion and kaon masses between the two
  spacings rather than kappa values.
- beta = 2.00 (c_SW = 1.654, a of about 0.078 fm **[D]**) is a cheaper fallback with a smaller lever
  arm. Spacings finer than beta = 2.05 do not fit L of about 2.2 fm on 32^3. PACS stout-clover
  ensembles use a different action and should not be mixed in.
