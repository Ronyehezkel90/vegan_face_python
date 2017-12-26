import sys

try:
    script_name = sys.argv[1]
    if script_name == 'count_recs':
        print '1'
    else:
        print '2'
except:
    print 'problem'
