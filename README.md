# Solving p-median Problems

This repository contains source code for solving a p-median problem using:
1. Mixed Integer Linear Programming (Exact Solution), mip.py
2. Heuristic Algorithms

    a. Alternate Selection and Allocaiton (Maranzana.py)
  
    b. Greedy Addition (Myopic.py)
  
    c. Global Regional and Interchange Algorithm (GRIA.py)
  
    d. Fast Interchange (FI.py)
  
    e. Exchange Algorithm (TeitzBart.py)
  
3. Distributed EM-FI Algorithm (EM.py and FI.py)

The algorithms can be called using PartitioningManager.py. 

The algorithm classes require the destionations to be initialized. Each destination should contain atleast the x,y coordinates and demand. 

The repositorey includes test datasets along with min cost solutions. 
