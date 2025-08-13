# ACTS Integration for ATLAS Phase-II Track Reconstruction

https://indico.cern.ch/event/1488410/contributions/6562807

## Plots

- Perf evolution (paul)
- Cluster plot including Algo time pix + strip (carlo)
- One seeding plot after restriction of which layers are used (+ doublet / triplet cuts) (noemi)
  - Maybe execution vs number of seeds before and after
- Efficiency ACTS vs Legacy fast config (pf/andi)
- (Maybe) resolution d0/z0/pt vs eta (pf/andi)

### Clustering

- done by carlo
- used 1200 events from mc21_14TeV.601229.PhPy8EG_A14_ttbar_hdamp258p75_SingleLep.recon.RDO.e8481_s4149_r14700 
- root script `./drawTimeVsClusters [PIXELALG|PIXELTOOL|STRIPALG|STRIPTOOL]`
