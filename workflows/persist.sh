#!/bin/bash
# Persist RHadronSpectrum work off the AP scratch space (idempotent, incremental; run periodically).
#   home (~/rhadron_persist, small + critical): correlators, blind secret, renders, benchmarks, workflows/logs
#   OSDF project area (large): gauge configurations and checkpoints
# The git repository (~/RHadronSpectrum) holds code, configs, logbook, results JSON and figures.
set -u
S=/scratch/llee/rhadron
P=$HOME/rhadron_persist
O=/ospool/uc-shared/project/futurecolliders/llee/rhadron/configs
LOG=$P/persist.log
mkdir -p "$P"/{correlators,blind,renders,benchmarks,workflows} "$O"
exec >> "$LOG" 2>&1
echo "== $(date -u +%FT%TZ) persist start"
cp -p "$S/blind/secret" "$P/blind/secret" && chmod 600 "$P/blind/secret"
cd "$S/data" || exit 1
for e in qA57 qA60 qA62 dB700 dB570 dB410 dB300 dC56 dC54; do
  [ -d "$e" ] || continue
  mkdir -p "$P/correlators/$e/gluelump" "$P/correlators/$e/quark" "$O/$e"
  rsync -a --prune-empty-dirs --include='*/' --include='*_glue.h5' --exclude='*' "./$e/" "$P/correlators/$e/gluelump/"
  [ -d "$e/quark" ] && rsync -a --include='*/' --include='*.h5' --exclude='quda_tune/**' --exclude='*' "$e/quark/" "$P/correlators/$e/quark/"
  rsync -a --prune-empty-dirs --include='*/' --include="${e}_s*_c[0-9][0-9][0-9][0-9].h5" --include='*_ckpt.h5' \
        --include='*_hmc_log*.jsonl' --exclude='*' "./$e/" "$O/$e/"
done
rsync -a "$S/data/render/" "$P/renders/"
rsync -a --prune-empty-dirs --include='*/' --include='*dag*/**.dag*' --include='*dag*/**.sub' --include='*dag*/**.yaml' \
      --include='*dag*/**.config' --include='*dag*/**.out' --include='*dag*/**.err' --include='*dag*/**.log' \
      --include='*/logs/**' --exclude='*' ./ "$P/workflows/"
echo "== $(date -u +%FT%TZ) persist done; home $(du -sh "$P" | cut -f1)"
