# Release inventory

ME 306 Advanced Thermodynamics — SMR sCO₂ Brayton cycle project
Archive:   ME306_sCO2_Brayton_RELEASE_2026-11-09.zip
Packaged:  2026-11-09T14:10:35Z
Root:      Programming/   (extracts to one directory of this name)

Files:     207
Bytes:     3,542,740 uncompressed

## Verification performed on this exact tree

| Check | Result |
|---|---|
| Test suite | **41 passed** |
| Document claims checked against saved results | **39 checked, all consistent** |
| Studies executed | **9 of 9** |
| Source fingerprints across all manifests | **identical: 65f1e4b8ee4f7fb1 (73 source files)** |
| Master document | **126 pp, 0 undefined references** |
| Final report | **18 pp, 0 undefined references** |
| Generated tables | **12** |

## Contents

| Directory | Files |
|---|---|
| `(root)/` | 2 |
| `brayton_cycle/` | 6 |
| `cycles/` | 40 |
| `documentation/` | 78 |
| `project/` | 29 |
| `reports/` | 5 |
| `results/` | 29 |
| `tests/` | 9 |
| `tools/` | 9 |

## Verifying after extraction

```bash
cd Programming
sha256sum -c <(grep -E '^[0-9a-f]{64}  ' INVENTORY.md | awk '{print $1"  "$3}')
pytest
```

Windows: `Get-FileHash -Algorithm SHA256 .\cycles\solve.py`

## SHA-256, size, path

```
7089f548b17dd054778a358f2efccd79ad1c4c75916eb08831dc9ddbb821ef97       1085  .gitignore
df4e765017ab7a195c46fac89a3d723917e8d627c2dfc575bb06a7c6330c4842       6492  README.md
a2e35d0e407e5e75de6266c6c004ce9ea8feff5c752d3b4cb7da164e52c94bd5        696  brayton_cycle/__init__.py
fac45803a4beda31456c287401bab8aba9c5a1e7e1369baec161c0a2e3fa4764       1168  brayton_cycle/intercooled.py
52cf50162627070d9740d045ec00785d3aa258031fb07738fcf8e848a1483d15       2543  brayton_cycle/partial_cooling.py
7622c3130fa65cbee25ba6ff111ab291eb7290ea615eb4eabb805d72facf5507       1648  brayton_cycle/recompression.py
6d3f8dabd056550d6da3bc12bf5d84756cf50fd54d8aa90cbdefb4a2d8a6369d       1006  brayton_cycle/recuperated.py
da3137c38bc8cafb81a63f9b59b4bf5b885fccbc380219a5dc1cfb79cd6ff7a2        672  brayton_cycle/simple.py
363e968579489d2a2c1b2e28f47ec2236e83e8312fd4ceaca2fd0fc4b9c88b74       4618  cycles/README.md
924f6d9ef0de27b467a5bb551f0be7ef36398cc186fb615c22aec0093c60f2a2       1281  cycles/__init__.py
226014bf7afefb0f76ed1fe53247ea238a4d2cf1115107b900fdc53b65d083e7       1207  cycles/blocks/__init__.py
5f377036056cfbf2aecede8ebcf5b2f94c999ed872aa5678f912c8956904f0b8       3094  cycles/blocks/base.py
8dae1b82939e0a7650d4c483ffdd053bb49d4ad19225dc458054f047308665c9       1726  cycles/blocks/compressor.py
02263bd5c7db3b3e2894e0bb429f07925dac202abbb0b96509f4626bd4c11f48       3900  cycles/blocks/cooler.py
34cf07d21f7250ce01c20516a7b78d80290629098fb7ac0a07ea871d60639614       6343  cycles/blocks/heat_exchanger.py
5bfad6196e343c033baa69eb1af27cccc683462dbf27e4ffabbced311ad34575       2384  cycles/blocks/heater.py
d1d26cf2fd77455cf2b896cf5641c694c634681427f8cabfef2db431842cae33       1675  cycles/blocks/mixer.py
09316b21e4c568af575ca0e902fcf60177d33654a1e0d549df2539fe878c0b91       1205  cycles/blocks/splitter.py
1ff040b71f0110dec14a5ebe236de807692b06d557b38b53ccd75b3dda68675a       1247  cycles/blocks/throttle.py
5c685b29654cd5ef1febc8b1d2d2de5d53d9cf000dcbdadca898d0a9225dd7bc       1346  cycles/blocks/turbine.py
5652e78f498263489e262689aae4db195c133cebaeb6975bcb8e646ff79e71cb       4175  cycles/case.py
c35316780259d8298674a559797e7620ab0c8e903c51104c9c9b31616b0f2339       4678  cycles/flowsheet.py
dd1d162a7ef8236ad6b56e80c427b47ad0fc4472e0012a5b6cc04e1f9f7e83d6        282  cycles/numerics/__init__.py
acf02d08fb8f0425f155d4cb60e8879a0477c253831d4249ebdaf94e2807a970       3958  cycles/numerics/roots.py
f30e34e1c316600743165a662c539d9f9d9bbe25871d76026f38488170e03584        254  cycles/passes/__init__.py
99d5d83fee5d45bdb3347aa39eb5a8067a10a4a924a736227126ea110a627944       3204  cycles/passes/flow.py
b89f94765ea1e7f47b8b557d09b1ac4b2e045006a91dd3f22b68fc52ca2e409c       2107  cycles/passes/ordering.py
18c2ba97cbb90d7851ee73799943fdfafed9a9b76f14704d9410b64233a982ce       3637  cycles/passes/pressure.py
15504471137250c33630ddd141096631d0f700d3e29b060073fd924ebdd0cb91       2012  cycles/passes/tear.py
39d2bb379a5fb37cc77263181e4fd6e45b395df5af229ba75e31229943cba551        375  cycles/physics/__init__.py
6afaa7d516735834f85e648326d2adbc31d14697b724656e9cfc1c605dd4efb8       5389  cycles/physics/coolant.py
412c9e1e3c2cded253693667e7c384fef6c4d781e85de662328fcaf4fc4d72da      14679  cycles/physics/exergy.py
aa5fd7c1b87f576ce84e736bba07d29db50337ee093c6df0e9cf7ce8f8e02cf4       3164  cycles/physics/hx_limits.py
fce58c0b84ad39bbdf429d539c126c58660a9decd9ee4a5266d081f1b9391f44       2086  cycles/physics/hx_profile.py
b70da9f55f590cf777d431951cb0c269719ddeea5f315927e08074ef00172a12       1329  cycles/physics/hx_sizing.py
89eeb3442f73d0d5b42cdb6a0d339ce8677e59abb34c4d37c212942b8d56a97b       3740  cycles/physics/hydraulics.py
6c4599f257d3fbe02a5bb6c24c302e34dc487b444f1239183eb2e47162bc2852        929  cycles/physics/isentropic.py
b5683f3bec8443344fb4d952fd8a08d2b5d9306e54aa43c3e1dff4c1282bbd4c        699  cycles/physics/mixing.py
d1f33da12c3611998c23d4947f104380154daa406ba60ddd60e23ab02b01fb2c        649  cycles/physics/pressure_drop.py
1708e328412fa2ae583c6d088e7d33d1cf3294592f973bb88ae4fead1e02c08f       1062  cycles/properties/__init__.py
98b202bda251f0813016e62c794c13c8b62013742d9cbe4ad14c6c3566c55e43       1738  cycles/properties/base.py
7bcf13e57b34c8d1a7568bc395cb2cbd4cfc22618d6466794a9ea07973013edf       1673  cycles/properties/coolprop.py
acc10fa3550d91d2925f132cb9c0dfe31da881559b65d4f6a872fe69a7c20ef2       2250  cycles/properties/idealgas.py
92fbc7a5ba8c0d16199648d129cce2535ecac7242118357d5c35ef94288e85c6       3127  cycles/result.py
585bf66063caec43c301f0eef51d6f1b198d656b6c788aab0deaeccc6529ec0b      11976  cycles/solve.py
7db4707e263574ef0def84eed07986f51206fb1b40bd29882a3f8c69f37b59d6       3045  cycles/specs.py
232c53ebf9b40aa08f6fe6fdc16cb957c0dfb15b9e9427560192c170c6407ec5       1242  cycles/stream.py
3077a96771ab5919ec8a1db762c66f05e7a200e1677617d4d866a86aca5352b7       1411  cycles/units.py
ad3960c9ab575daedb25c246607c70bbaeb07100b4d1bab6ea7bb548af6337f7     326735  documentation/SMR_sCO2_Brayton_Problem_Statement.pdf
cb37177f6e3c77ce06335ec20cab5e31fb94459a6e7e96dd8ed252c82faa608e      61242  documentation/architecture.md
f4095965fec3d1a89bcd5e7a886da71cd4694db87ce9052c80f6dadc93ca25ac       1896  documentation/latex/build.py
72bbe022460ab8fcedbf6cbf2476b4103c040a880fe8a0fba6064aa6ac789bfa        656  documentation/latex/code/bisect.py
d17de33dec8f1a02cb9d5d8a35cb8f97b59b9bac40bed42d420ba133093f31c4       1028  documentation/latex/code/case_baseline.py
ffc20780b0004cdf25885fd53d38c53751e5e527b0693dcf34ec2b9f6cbde921        886  documentation/latex/code/circuit_models.py
255f4ddc84cfff49d5f711efb105c24f5059c665e94a5a319b93cc6a15ab545a       1079  documentation/latex/code/compressor.py
9329e7e5a8b0f61a01d3f363dc4596579f103d7138e6772044b1d8f5ae32cd61       3075  documentation/latex/code/coolant_size.py
79b7fc9d733d00e79d5540d1b36dc278bac264020d4327aa727982cc9965a5e1        246  documentation/latex/code/coolant_specs.py
c1d44d7cd5653e0abc736cc8a1ebce5d8af6afba4dbd264aee45feeb85f86917        535  documentation/latex/code/dominance.py
0e7bfe9a16399235515cfebb7a531af422ed4e92212a5227433ad713aa23b819        486  documentation/latex/code/duty_limits.py
49b5ad216282e45ef17f278407eaa5b51b7868e47b809de30cc89bbd6b56ac38        444  documentation/latex/code/exergy_balance.py
95b66668bc0b4fab56b9ee8bda23e1b2ced1fa3f5036e79d97d36ef43258b5fd        470  documentation/latex/code/exergy_specific.py
ae70bbde50ef2d663eecf8e56586487723683b35a3122932a3ae645829e1e459       2012  documentation/latex/code/feasible.py
b704773a1695a6813c64ae2ad91196abc1246b6e7570a1a3ec3ccbad8de0e21c        114  documentation/latex/code/fixed_outlets.py
d15fb47ddd9c968169c2b48aca888f4fd88ce331e2a5727a29e6b878e4bb7a58        274  documentation/latex/code/flow_rules.py
1a9600ab80cf794d6788a104b62bac2c772c5ed6f609425c7deb2f09adf6b798        718  documentation/latex/code/hx_profile.py
378964ea248b50ad4bacd7bad069b965122e0288b8e09608590606144a384132        185  documentation/latex/code/hx_seek.py
0c8beac64aae9b232d057fbfc6c008edb267e8d81a573e1a69e429e1289518c7       1373  documentation/latex/code/hx_spec.py
d6a96df7976a5a905f9f19445273cfea906388a37c0bd4f6385d7e88e92f904d        363  documentation/latex/code/inlets.py
703871de79ccd8c7d474c1a69c0a7b23212fb2025e5b4145c19e65b934fc6813        301  documentation/latex/code/isentropic.py
4b04089bd96dfa0e707e8574fed6c2f48258fcb845a6667b15cdb94d00db2ace        679  documentation/latex/code/knee.py
597dab2bfd85548c02426635b08f96df3299699205a8d3253ff002d249217d6d        862  documentation/latex/code/layout_recompression.py
a47fad48669ab65d82370c6171d01393745d0b02885d229ed5e31f5a5fb3cbd7       1079  documentation/latex/code/mass_of.py
545260ac8bc73d548e9c7ab3b9e5a2b32d2ea8aece3979e99c6a2750f06f5e20        782  documentation/latex/code/metrics.py
0f3a6f7798d8d7976ff39cc5db8676f2114bee5e675d0dc9c8824121c51c5436       1322  documentation/latex/code/ordering.py
6967933831a74d2bdb3724b9d0b7fa2c092c1c0d564b021dbbe5c7c920f20779        373  documentation/latex/code/payback.py
a5ba5d428acefaf816e62b0cca489dcb069a88730a003f138905fbfa61e15bed        363  documentation/latex/code/pressure_propagate.py
2d15a667a22ce67bdf263f9b9cdf1abae608d528852e338504b5c67671c9ca88        346  documentation/latex/code/relation.py
2e0c58b203349f2edf142d808c8c2d62ae6945b0df0aa074ae635a7a80151346        290  documentation/latex/code/sat_guard.py
8f26f2758d962aaae65f4604fda0c685da7ee954388e71be3f10299f2973f511        740  documentation/latex/code/secant.py
59b931c79844f2bbc2a4e61f73cd2b529b93e31e5096f91d0d6f759412c4b40d        465  documentation/latex/code/solve_monotone.py
c6e886c37e6fbc071425bdcec52ae185df3e53bfb5a47c825fd54b02f2db0b17        654  documentation/latex/code/stream.py
f6cdaf2fda3b020a80f6e345e5629fc2d2a66b3d9a6e40d59ebe60d90cf2aee5        376  documentation/latex/code/subst.py
a548ee8894dc00d55663f27514857c89b819b37f9738aa6db674e6c22a3517db        438  documentation/latex/code/tear_guess.py
0f8f17cb98f4274ee7ba3e32b2cafdf4286a4679f27c017b5404a72fd5833021        719  documentation/latex/code/tear_loop.py
13e56a0446974a254f921facaa14c36a407ca3857836e64f1f7b1aec57b452b2        594  documentation/latex/code/ua_sizing.py
d594065713676a4504406d18ae86c5a698761978158709b4c020ded69fb0d77d       3224  documentation/latex/data/cp_co2.dat
16843cac503cdaa36068bb04eacd965de7c81a65f1438ea15b6fc8869ba91de4        210  documentation/latex/data/eta_vs_rp.dat
937df341888a13714853316cb223dd53d0be872df9bb4efeac1bbc06230d1754        188  documentation/latex/data/eta_vs_x.dat
9a8974776d76134df70c6bb3401ebd09ac7e63d475af4cdfc9842c14004b057b        324  documentation/latex/data/exergy_by_layout.dat
70831e30f5765544ca5b06d424e9f43aea9de201fa477ba7026e29977062be6c       1268  documentation/latex/data/exergy_vs_x.dat
0b097888e92aa135ca92be49e1261c5d48a72119d58430ab5bfeffd196c5c32c       2025  documentation/latex/data/pareto.dat
b1cd3bc222fb2c5d72b003d5d024d22d7c47bf044e81dba6ed7b56fd96e80d02       1160  documentation/latex/data/pareto_dominated.dat
57be9517b66547e05863f6b3439adb8cd24c88033b4ffc1279f891136dd21679        177  documentation/latex/data/pareto_front.dat
56b4534fe9f88080bbc8037c93407361cf9b5a2bbf1c37fe23dcbc740ad396d7        290  documentation/latex/data/pareto_infeasible.dat
3f9c99aafbfae34fb0228656e48ca1ba39050b41336be5b86829aa46014ca8f5         68  documentation/latex/data/pareto_knee.dat
0fa02ab28a0fd7d4b3a3f210c40085cfe0cb156446cc4d72f7f9d5a628e1bbb7       3236  documentation/latex/data/precooler_profile.dat
aa406a185fa5e326b6b0854c4b7f4395b850d76d0fd14f3735e515b53ddbe4c1       3531  documentation/latex/data/recup_profile.dat
8a06e132af31c454fcaf9e52511f389b6a4809419e02ec229e05af70e8d995af         66  documentation/latex/data/ts_branch.dat
83545711bf99c6571ef62beb1edfe730982345571d454509a067ceeba130fb10        204  documentation/latex/data/ts_path.dat
64d7e75a5c23d766760a72560e50a0b55c3df0b5b040e953340b39e2ece70f69        430  documentation/latex/data/ts_recompression.dat
8c09ed55c882b0f3cce069778ee5303ab61baace90ec66469c0222ad928e9b22        813  documentation/latex/data/ua_vs_eps.dat
76b92a195514253a83d2c71ea8854089bbe043f904896ba502e695c90228e536       1262  documentation/latex/diagrams/intercooled.tex
cd6e56eb2b3d5867f4b255420621b31568dbea478c9ad4f8f199d71336dbe3db       2800  documentation/latex/diagrams/partialcooling.tex
24d4854e1e70ec76b701f85df94572a36d8a23aa81bbb6f267f5a4e1d88c79d9       1108  documentation/latex/diagrams/pipeline.tex
65ab6fc45a0f34f416c97f2a419436e2e9c65c6dde807bbb36860976d4aa4681       2045  documentation/latex/diagrams/recompression.tex
1b512927af1fef1fb8e78675f0577158c74eabfa3b5af03ce0ec0bb2379f42e3       1028  documentation/latex/diagrams/recuperated.tex
8b1b3f8a9096b59ed943172864baa9dd930371171f4c3075414e4a3bfea8e801        522  documentation/latex/diagrams/simple.tex
5512b98fc6ac8823808c68a114e02a45521a263b75755d35edd31d0eb7e2621e        555  documentation/latex/tables/coolers.tex
94657d85404267fe4da1bc52f2366bcdc097b735e6d52bb0dec492648e26e936        346  documentation/latex/tables/exergy_balance.tex
4daae22767b2a75627d6da049d64597a474871e6aa7250be157ead22aef7ceb2        437  documentation/latex/tables/exergy_components.tex
844ec7a45aec30c4164623a06fb1d3922001571d8dcbdd84a312a0dede167297        574  documentation/latex/tables/intercooling.tex
b23830c4077c4884c07e82c1df89cd0e2e24bb10f9c8e6462c6b0951d7ebffa0        386  documentation/latex/tables/layout_comparison.tex
f5faf6d2dd2291b6e869e99936a66f3f1dd75ba08d2adeb5ea93d7e8532701fd        515  documentation/latex/tables/pareto_front.tex
6fa325a491422add05b93fd0b19d259739c21b09f2e699b6118d989cd2aa5c5b        380  documentation/latex/tables/partial_cooling.tex
cd58e2f722b1a08e752eb86aaefd0306c20412242a45be7fc036b6caf7f52360        432  documentation/latex/tables/performance.tex
e885eb2dc1fb0c2dffb0d4b5c49164b239a7b9a609340a79f0d97c339e2ca0bc        750  documentation/latex/tables/state_points.tex
565a84f3006a4c176376ad2cc613a62f248ea053f6e8cd153713693e00d60084        881  documentation/latex/tables/tolerances.tex
17ad5e580911e170df04065df4aafd7ab01ac7d1ebf0ff54d2b0538a825f1f1e        365  documentation/latex/tables/total_conductance.tex
26765eb257e551c020ac752df4da218bd42dbe6d6fa3e45aa495065c9de404e4        486  documentation/latex/tables/water_sweep.tex
2504499f5ee44b72830facbf6e3220a606450b6785def2776cf54e9f74b2ee66     947192  documentation/latex/theory_and_implementation.pdf
89d37fb7f14651d909e198bf175fbf33bb746f8ced30f88e7b6a866cb01288de     227373  documentation/latex/theory_and_implementation.tex
7d07391d5e204c9663638c5258bcaff73db4a504aaf30d3a38fcbc68e0e7fd26       4528  documentation/migration_table.md
4cb7f104430381367c086dc6038fccbdca526aac3038fab7777540926c999606      93315  documentation/project_tracker.md
9b5ca8e979c4cae09a2bd654ac1f54b8dd8ebf97c8a35058669110241c4ea5c8      18852  documentation/registers.md
2504499f5ee44b72830facbf6e3220a606450b6785def2776cf54e9f74b2ee66     947192  documentation/theory_and_implementation.pdf
8265d2a1910cbaf79082c89b07b766a0301bd4c551c714a7dfe56a00df704666      24976  documentation/usage.md
992536d07d4fc39bcc3f669aae75fba610d25ff30c0d17e19bfbe1c9a3772e3a       3327  project/README.md
c2825d9e4e2b3e732c4014028a8193b4fc621eaf70ff41ffe12825e28aa1b16f        256  project/__init__.py
c8c9998e4d3a21474285341e9a93833c67ddb31c315a7c93f09bc5bcdfb1cd53       1167  project/assessment/__init__.py
06129b69b62f66a956a502974a937ee174435d0d35201d011f6be5d541cc1e2d       3414  project/assessment/cost.py
2b2631ca20398df83651711b011b41165ab61e4d3eda04e1f15b09af72d718c5       3861  project/assessment/mass.py
a9785855ac18bb8207d00b1a2331d3e320bcdaf275c64b6e17d1d32fd4b30b0f       4065  project/assessment/metrics.py
c905c77b58bf33a6084b49d24860ac3eb86ec0575c44dd9981a0f8dfb62fa55b       6594  project/assessment/moo.py
ed9636d740b0094b81eefc0803445e6783e140e6a4468488da8373d9625d6d47       1523  project/cases/__init__.py
297776a174c9672134a313569a9de558cc16ec381fed6c4f7e149f35274e1422       1437  project/cases/air_brayton_ideal.py
1d83a4e2bab43a45e458e64d24099229522098c239a564107c7847b362fe3284       2877  project/cases/literature.py
8f7e3b0dcdc316c22be1849467bbcab880b0811f1b6ac69d393e11bdbe4dbbd8       1691  project/cases/pdf_baseline.py
85b2c264016741caa71933f85699de856ddcb0846d3a215591d66f4a5a6acde0       2572  project/cases/pdf_intercooled.py
582618eaa3ba48450f1f79ea2f1bf88f50d198c65cf7b62b026bfa796319d377       1940  project/cases/pdf_partial_cooling.py
32d837a8cb585c9ee82ae0663cba34f22e9d070a89d1cfeec8674236ccf55701       1605  project/cases/pdf_recompression.py
810adf5ba02641f3589016b8b42feecc32e65eefb13540316e2fbc457a714099       4488  project/cases/pdf_watercooled.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855          0  project/studies/__init__.py
97d00cf28a464afdab18fea3fbb0aa54898f08a9b221708cc2f3c051e02befb1       5119  project/studies/_io.py
6d8070adbbc8e51d3f88ad9842344ebe57763ae67a705a7db50fcab75464b9c0       1529  project/studies/check_nodes.py
1a3ae6e86d9d902cbb608c7456145c1cba925a29b6b6000418a24e547338a189       6165  project/studies/compare_layouts.py
032db062f0799785725f1b0bf10f0361b207e168875969538800649844db2d54       8543  project/studies/cooling.py
e38ba26507d3432571957966f315a83f36fc0fa6fe37da78020fefdb2b3bc6bb       9868  project/studies/exergy.py
1a134527faf246655d191b07ccf0955036168836903e95e58451c24b05d43523       8341  project/studies/intercooling.py
8856b6c5a074444b4eec286acc518bff58cd65d077c836a2086b6f07a1d5d64f       7915  project/studies/partial_cooling.py
10a13e6db5cee2bd2345a655e2e3d021225608665af5077123027846796bb2a8       2689  project/studies/precooler.py
499e6a9ca355c963ac75a24aacaaa49f4cae696063a9a0ec25727a2a4cb4a207       1614  project/studies/run_cases.py
4a2c47e3a3161592f7f868158f868dc64daf79b7f07bf457a0f41e2dc8b848d7       7195  project/studies/selected_design.py
b89efce42909edb8dd87bf6112f04ed8041ad60251e1e06b2c378daad5f3efed       6095  project/studies/sweeps.py
39a54d4ab7ef8891bee6ed2d702ff0a9cda7667e64895fa955e38566331f448e      14349  project/studies/tolerances.py
80877359ebea07853678b507a6366ede2b8153b59f4fdf4cfc7a6652652b2aad      12461  project/studies/tradeoff.py
5a170a730a0851854785c81709c1cf6a925ae402718c24ab6b436b4715fa0e9e       3379  reports/_preamble.tex
f3cadf11d7a75560cd7d99be80626d8411a4c7d33eea7a7375b355e7840dca4d       1576  reports/build.py
a71bbb108ed53a10af801e6012d5c7ab78cf42614e8c108852cab84926aca5f2     372524  reports/final_report.pdf
8758b2f7a8927340fd848ee9eacc947152ebf2dd57a353bf93bd096e7c51b84a       2661  reports/final_report.tex
eefe1e71bff78c4fb33ba4c37d51b27a25312392d4ea7a955edd5058a7bdb2c6      41480  reports/report_body.tex
484a92a42944f1f2aa66aca8a58d6130734445a252a485255dcca9db5372303a       4458  results/README.md
d5e42a9b9f77b9baee53aea6f2c15dcd7de9c24825cef367e54adb1840717434       1584  results/cooling/manifest.json
f71da89707b406223fdf5cddacb6946157cc4961126458b217de587cacaff50d        408  results/cooling/per_cooler.csv
8abea478e8346eed86895f7f9bd547cf8b87cb5f98c7c943988b5a1db0cf120c        465  results/cooling/water_sweep.csv
0c823912c9be2d83edcebd39add138fba2024e0c3e91c8b3b6cea4f5e209529d        394  results/exergy/balance.csv
5e3848a02df1c860a0b087ddb89054aa6888857e459aaa6a2b2e7818110a7427       2040  results/exergy/by_component.csv
ef91a910aedde50b806ca669b80bda77275a541a8dbe7b6c3392437f4aae965d       1555  results/exergy/manifest.json
91d4a734ac66babfbc9d0e6e5eded859c3d1a259bfbb7520c64fc36a35a3903b       1956  results/intercooling/manifest.json
2b3b2d11479838a9127a131acb310e3f232fb0ef8d8c0b755cec78d01750ef3d        588  results/intercooling/pressure_sweep.csv
14329f25f7acbe6397df5c9fdc89af81bed513b5e9b27a7c40269f82bad4f75f        536  results/layout_comparison/layouts.csv
678afcfdf3fbf5261f5d6cba0a43e019f97471f97060e7138235558208472cff       1539  results/layout_comparison/manifest.json
580c881125542bc1667d0c8340c47d0cb88ec8f2de26f01540d97c5643fd73f2       8699  results/multi_objective/candidates.csv
a8b12cb3413d54c22f1475784f56d3d10ba4c2f7ccd0439579ae186f7ca0fd15       2874  results/multi_objective/manifest.json
c09f19127ae0715f0b4f322de128eb047e879bc3f16a7ce5f1f008dbea05733e       1241  results/multi_objective/pareto_front.csv
8abe6ca5da9e0e5e20c3cbd6f14ea01898ed85612069ae6009d896cc15ccd01a       1438  results/parameter_sweeps/manifest.json
e501150d798844b79a40ad755d583c90c2188d9a6af32a0a9398f8fda121fed9        269  results/parameter_sweeps/pressure_sweep.csv
840f569df156593f676e51b8a2fa6391084cf4943092b9eeeeced963b3d6b336        224  results/parameter_sweeps/split_fraction_sweep.csv
b0bb41fa258959d49f77fc52995dd65c507dc7298c5165b6b472d20d28660871       2074  results/partial_cooling/manifest.json
53c16e020d18fc690c9079202446b18f575bf9861d893c8cf6fa82712d4f5d8f        502  results/partial_cooling/pressure_sweep.csv
676a4ad9206cd54ba1c00e70c665910c2be47dbbfb2f8b5c72d2545512a497e6        506  results/partial_cooling/split_sweep.csv
d82aa58d8be777f85c649aaeeb58de583f4f70186396e4c3debb5ba4c3ff1c4d       1703  results/selected_design/manifest.json
811bcaff246d9af6d8504c03d74604feb44d3fa9f8892c517d69b0e55429e42d        270  results/selected_design/performance.csv
36f4faa00ae57202bd8da75f20e04ecdfe0ca17a876c517a0095a3a4ae1c5a33        520  results/selected_design/state_points.csv
7d8efe1f1ac99067e91d96b54d17413e0ac1551bb3b451ddad9b51fcb5ad14ab         85  results/selected_design/ts_branch.csv
c111a14c4d8c9e72e78bb24f8931de21cda09f061bc8eebb5b3cfc4ab9df5982        219  results/selected_design/ts_loop.csv
a5ef9e05838847502048f06bc9d81054ac73e287bf87c18ee0d1b60e490631c6        243  results/tolerance_sensitivity/knee_stability.csv
0eb56ee7899efc638b4cc0eef7c7aba9fce09f8e764f11260884450e7d191d24       2789  results/tolerance_sensitivity/manifest.json
f73e6c75000a9a21c73441f4b31aa9c5fc4993d673cfbfe0d2fec46aa4d70866        293  results/tolerance_sensitivity/mass_propagation.csv
6390979c3a76585568adb906d80012c1e8d13ce542dfc367aafe995cdd55aa59       1032  results/tolerance_sensitivity/sweep.csv
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855          0  tests/__init__.py
b5091e40695de851ffcdc9becee1c1c0ee293d78603581a528c3ccf085534d4e       4075  tests/baseline.json
e43c388a2116b1f2ab42ae3d42824cccd00d767492ddbb620260adff1a7dc617        213  tests/conftest.py
601ac66b4e3bf062d05f9b332a35b93d8b2a1de102c8b99a8ec5d0b84216a104       1967  tests/test_regression.py
c772315eccb7283ea1e9efa398a6914955d79574c8af25bccd9b63335789988d       4040  tests/test_solver.py
3ac1b1191b24aab33c333aaacc9fa1c31edba5284553953e313a88994973d9ac       8251  tests/test_tables.py
442c008e9948a2ed2c6ff65635ebad470355e9a1102e52ca2ea97f3ddd5fd678       1314  tests/test_validation.py
1f520a9339281d0aff0eb7741c0c2191309a3e8e9f9ec2ea8024762fdbe6bf57       6514  tests/validate_exergy.py
edcae4efbd0d144523d9b3dbd05de07dfe2d8ae78a9a704192fe1f0db067f720       6701  tests/validate_literature.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855          0  tools/__init__.py
a7e553764c4ab3e112b7cc1c55793edd6645a7c52e1e28f61960e2e0931f742b      10642  tools/check_consistency.py
b5d1f5128e24905b7b4cc47cb36920fecdbb7a83d67bc2849957107b68f8376d      14245  tools/make_architecture.py
4c9af2021df1254752177fc5350ae8f022aaf36f8822f2ae129f68be48cca6cb       1515  tools/make_baseline.py
8a73669abe63ba4ff5eab6abc81926ec6d69530ce012600b19f9b6bce266b931       6294  tools/make_code_snippets.py
63df1cf3433a2794f95793fbf027633d418296b12870a2d9f74ece8f044515b8      10041  tools/make_figures.py
9753d651e2af4db68e903ccb85c876a330340980273ec19684aaebe1123cf879      13071  tools/make_registers.py
c762a10113ab623fc9d59a95f9408a38f1bbf2b67a87022caad9c9f2b607aa2d       8015  tools/make_release.py
200fb423ac9b6a3ff909d43c92e74e9840d3ef361b6277c996ecbffbb0e68d8a      11098  tools/make_tables.py
```
