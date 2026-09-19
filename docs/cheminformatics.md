# Phase 4 Cheminformatics

RDKit processing preserves raw structure input and stores a derived normalized representation separately. PSMILES is parsed as an RDKit graph and dummy atoms are retained: attachment-aware Morgan fingerprints use radius 2 and 2048 bits with `wildcards_retained`. Two attachment points are common but not universally required; other counts are `partially_valid`, not automatically invalid.

Repeat-unit structural similarity is Tanimoto similarity between those fingerprints. It is not polymer-material similarity and does not encode Mn, Mw, dispersity, DP, tacticity unless present in supplied graph, composition/sequence statistics, block length, morphology, crystallinity, processing, formulation, fillers, crosslink topology, or measurement conditions.
