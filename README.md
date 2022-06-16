# TFRRS-Graph-Mining-Project

Individual class project for Graph Mining at RPI by Connor Wooding

***Note:  This is a very rough draft project as it focused more on learning about web scraping for graph creation and graph mining techniques as opposed to creating a well-designed out program.

## Predicting Cross Country Results with PageRank
The first part creates a "competition network" with edges between runners who competed against one another in a given cross country season.  The program uses an in house web scraper to pull all competition results from a given division and year to create this network.  It then applies various PageRank algorithms to create a prediction for the National Competition.

## Analyzing Track Event Patterns
The second part is a track list analysis that takes any TFRRS Top 100 Track List (Indoor or Outdoor) and creates a grpah that represents the connectivity of any two events.  It does so by creating a bipartite graph and applying various algorithms on that data.