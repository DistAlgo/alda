This Alda test suite contains all of the OpenRuleBench benchmarks described
in the WWW 2009 paper (https://www3.cs.stonybrook.edu/~kifer/TechReports/OpenRuleBench09.pdf) 
except two tests that has non-stratified negation (the win-not-win test and the MS test).

In order to run these tests, the following steps are necessary:
 * Install Python 3.7.x
 * Install DA-rules as described in: https://github.com/DistAlgo/da-rules/
 * Install XSB from http://xsb.sourceforge.net/ and add it to your path
 * unxz all of the files in data_raw (these are the data sets and have been xz'ed for ease of upload/download)
 
Then each test can be run via the following generic command:
 python3.7 -m da --rule run_tests.da --testsuite testsuite_name --data datafile_name --query query_name

The query argument can be omitted if the query name is query.

Below we show the lists of test suites, the included data files for each test suite and queries possible for each test suite.

  * Test suite: join1
    - Data sets:
      - d1000_relsize10000_xsb_cyc
      - d1000_relsize50000_xsb_cyc
      - d1000_relsize250000_xsb_cyc
    - Queries: 
      - a
      - b1
      - b2
      - bf_a
      - bf_b1
      - bf_b2
      - fb_a
      - fb_b1
      - fb_b2
  * Test suite: join2
    - Data sets:
      - join2
    - Queries: 
      - query
 
  * Test suite: join_duplicate
    - Data sets:
      - d1000_relsize10000_xsb_cyc
      - d1000_relsize50000_xsb_cyc
      - d1000_relsize250000_xsb_cyc
    - Queries: 
      - a
      - b1
      - b2

  * Test suite: lubm 
    - Data sets:
      - test_10_univs
      - test_50_univs
    - Queries
      - query

  * Test suite: mondial 
    - Data sets:
      - mondial
    - Queries:
      - query
  
  * Test suite: dblp
    - Data sets:
      - dblp  
    - Queries:
      - query
  
  * Test suite: tc
    - Data sets:
      - tc_d1000_parsize50000_xsb_cyc 
      - tc_d1000_parsize50000_xsb_nocyc 
      - tc_d1000_parsize250000_xsb_cyc 
      - tc_d1000_parsize250000_xsb_nocyc 
      - tc_d1000_parsize500000_xsb_cyc 
      - tc_d1000_parsize500000_xsb_nocyc 
      - tc_d2000_parsize500000_xsb_cyc 
      - tc_d2000_parsize500000_xsb_nocyc 
      - tc_d2000_parsize1000000_xsb_cyc 
      - tc_d2000_parsize1000000_xsb_nocyc 
    - Queries:
      - query
      - bf
      - fb

  * Test suite: sg
    - Data sets:
      - sg_d500_parsize5000_sibsize1000_xsb_cyc 
      - sg_d500_parsize5000_sibsize1000_xsb_nocyc 
      - sg_d500_parsize10000_sibsize2000_xsb_cyc 
      - sg_d500_parsize10000_sibsize2000_xsb_nocyc 
      - sg_d500_parsize20000_sibsize4000_xsb_cyc 
      - sg_d500_parsize20000_sibsize4000_xsb_nocyc 
      - sg_d1000_parsize5000_sibsize1000_xsb_cyc 
      - sg_d1000_parsize5000_sibsize1000_xsb_nocyc 
      - sg_d1000_parsize10000_sibsize2000_xsb_cyc 
      - sg_d1000_parsize10000_sibsize2000_xsb_nocyc 
    - Queries:
      - query
      - bf
      - fb
   
  * Test suite: wordnet
    - Data sets:
      - wordnet
    - Queries:
      - sameSynsets 
      - gloss 
      - directHypernym 
      - hypernym 
      - directHyponym 
      - hyponym 
      - directMeronym 
      - meronym 
      - directHolonym 
      - holonym 
      - directTroponym 
      - troponym 
      - directAdjectiveClusters 
      - adjectiveClusters 
      - antonym
      
  * Test suite: wine
    - Data sets:
      - wine 
    - Query:
      - query
   
   * Test suite: nonsg
     - Data sets:
       - nonsg_d500_parsize5000_sibsize1000
       - nonsg_d500_parsize10000_sibsize2000 
       - nonsg_d500_parsize20000_sibsize4000
       - nonsg_d1000_parsize5000_sibsize1000 
       - nonsg_d1000_parsize10000_sibsize2000
    - Queries:
      - query
 