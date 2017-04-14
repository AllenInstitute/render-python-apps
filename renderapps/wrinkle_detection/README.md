### Wrinkle Detection

This is where we will be developing workflows to deal automatically with wrinkles in datasets.

The high level plan is to accomplish this in 3 steps.

1) Identify tiles likely to have wrinkles
         a) look at residuals of point matches
2) Take a tile with a wrinkle in it and split it into K pseudo tiles using masks
    a) using multiple hypotheses ransac with tight epsilon numbers
3) Recalculate or resort point matches from the k pseudo tiles into the point match databasse
4) upload the pseudo tile definitions to render