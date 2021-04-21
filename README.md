# simpson-reversals

Generates and visualizes indefinitely many Simpson reversals.

A Simpson reversal is when an association between two variables changes sign when you condition on the value of a third variable, no matter what the value of the third variable is. For example, in a drug trial, the recovery rate is higher in the treatment group than the control group overall, but lower among men *and* lower among women.

In fact, you can get indefinitely many Simpson reversals. For example, comparing treatment group and control group, there might be:
  - overall, a lower recovery rate
  - in each of two sub-populations, a higher recovery rate
  - in each of four sub-sub-populations, a lower recovery rate
  - in each of eight sub-sub-sub-populations, a higher recovery rate
  - and so on.

In the .py file, the two key functions are: simpson_tree, which generates an example of k reversals for any k, and draw_layers, which visualizes each reversal. The jupyter notebook contains the code, plus some explanation.
