This folder containes the input files and the best output results for the following problem sets:
1. n = 2437, p = 600
2. n = 2774, p = 700
3. n = 4850, p = 1200

Input file description: 
--> Each row contains the id, geometry (boundary), centroid (Point) and demand of a destination. 
--> The geometry and  centroid are in the postgres Geometry types, MULTIPOLYGON and POINT respectively. 

Sources file description: 
--Destination Id, Source Id mapped to the the destination, Destination Centroid. and Source Centroid. 


Min Cost Solution: 

1. n = 2437, p = 600, Cost Function = 12252623.26
2. n = 2774, p = 700,  Cost Function = 10119780.92
3. n = 4850, p = 1200,  Cost Function = 11379359.39

The cost function is the demand weighted distance between the destinations and sources. 