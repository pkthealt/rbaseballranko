#########################
# YUNG PARK POWER RANKER
#########################
''' Uses data from fangraphs-created csv's to make baseball power rankings'''
###############################################################################
# If you're reading this on github please ignore every terrible awful thing I
# did here. It's very quick and dirty and I know that.
###############################################################################
import csv
import operator
from prettytable import PrettyTable
# 0- Team Name, 4- Runs, 7- BB%, 8- K%, 12- OBP, 13- SLG, 15- wRC+, 16- BsR, 17- WAR
bcols = [0, 4, 7, 8, 12, 13, 15, 16, 19]
bcolv = ['R', 'BB%', 'K%', 'OBP', 'SLG', 'wRC+', 'BsR', 'WAR']
pcols = [0, 7, 8, 9, 15, 17]
pcolv = ['K/9', 'BB/9', 'HR/9', 'FIP', 'WAR']
fcols = [0, 10, 23]
fcolv = ['DRS', 'DEF']
WEEK = "./24/" # CHANGE THIS TO GET PROPER FILENAMES
#PATH = // maybe useful for the future
# These are for the past week
P_COLUMN_KEY = []
F_COLUMN_KEY = []
B_COLUMN_KEY = []
#PITCHER_STATS = []
#FIELDER_STATS = []
#BATTER_STATS = []

# These are for the season through this week
P_COLUMN_KEY_O = []
F_COLUMN_KEY_O = []
B_COLUMN_KEY_O = []
#PITCHER_STATS_O = []
#FIELDER_STATS_O = []
#BATTER_STATS_O = []

# the key lists are unused, actually all the empty lists are unused

def readFiles(file, statType):
    with open(WEEK + file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        ret = []
        temp = []
        for row in csv_reader:
            if line_count == 0:
                #B_COLUMN_KEY += row
                line_count += 1
            else:
                filtered = []
                if statType == "Batter":
                    #print(row)
                    for i in range(len(row)):
                        if i in bcols:
                            #print(row[i])
                            filtered += [row[i]]
                    ret += [filtered]
                if statType == "Pitcher":
                    for i in range(len(row)):
                        if i in pcols:
                            #print(row[i])
                            filtered += [row[i]]
                    ret += [filtered]
                if statType == "Fielder":
                    for i in range(len(row)):
                        if i in fcols:
                            #print(row[i])
                            filtered += [row[i]]
                    ret += [filtered]
                line_count += 1
                #break
        #print(B_COLUMN_KEY)
        #print(f'Processed {line_count} lines.')
        return ret

def calcOPS(teamStats, cols):
    '''Calculate OPS by combining OBP and SLG'''
    # assumes OBP and SLG are always adjacent in the list and not at either end
    OPS = teamStats[cols[0]] + teamStats[cols[1]]
    return teamStats[:cols[0]] + [OPS] + teamStats[cols[1] + 1:]     

def trimPct(teamStats, cols):
    '''Remove the space and PCT sign at the end of stats that need it'''
    temp = []
    for i in range(len(teamStats)):
        if i in cols:
            teamStats[i] = teamStats[i][:-2]
        if i != 0:
            temp += [float(teamStats[i])]
        else:
            temp += [teamStats[i]]
    #print(temp)
    return temp

def cleanBatStat(stats):
    '''remove the Percentages, convert to numbers, convert to OPS'''
    cleaned = []
    for team in stats:
        cleaned += [calcOPS(trimPct(team, [2, 3]), [4, 5])]
    return cleaned

def cleanPitchStat(stats):
    '''this works for pitching and fielding stats bc they're all floats'''
    cleaned = []
    for team in stats:
        temp = []
        for i in range(len(team)):
            if i == 0:
                temp += [team[i]]
            else:
                temp += [float(team[i])]
        cleaned += [temp]
    return cleaned

def minBest(stats, index, rang):
    '''calculates adjusted points out of of 10 where smallest is best'''
    for j in range(len(stats)):
        stats[j][index] = 10 - ((stats[j][index] * 10) / rang)
        
def maxBest(stats, index, rang):
    '''calculates adjusted points out of of 10 where largest is best'''
    for j in range(len(stats)):
        stats[j][index] = (stats[j][index] * 10) / rang
        
def adjustForNeg(stats, index, m):
    ''' adjusts values for negative numbers'''
    for j in range(len(stats)):
        stats[j][index] = stats[j][index] + m
       
def findMinMax(stats, index):
    '''find the highest and lowest value of a stat for normalization'''
    l = 1000
    h = -1000
    for j in range(len(stats)):
        if stats[j][index] < l:
            l = stats[j][index]
        if stats[j][index] > h:
            h = stats[j][index]
    return h, l

def normalize(stats, statType):
    '''normalizes the stats to an out of 10 value'''
    for i in range(len(stats[0])):
        # this is going stat by stat as if they were columns
        if i == 0:
            pass #ignote tema names lul
        else:
            high, low = findMinMax(stats, i)
            #print(high, low)
            rang = high - low
            if low < 0:
                adjustForNeg(stats, i, -1*low)
            #for j in range(len(stats)):
            # if you want to change the stats involved you have to adjust these
            if (statType == 'Batting' and i in [1, 2, 4, 5, 6, 7]) or \
                (statType == 'Pitching' and i in [1, 5]) or \
                statType == 'Fielding':
                #print('here')
                maxBest(stats, i, rang)
            else:
                #print('here2')
                minBest(stats, i, rang)
def calc(bat, pitch, field=""):
    '''calculates the overall scores, adds them to a dictionary'''
    ret = {}
    for i in range(len(bat)):
        for j in range(len(bat[0])):
            if j == 0:
                ret[bat[i][j]] = 0
            else:
                ret[bat[i][0]] = ret[bat[i][0]] + bat[i][j]
    for i in range(len(pitch)):
        for j in range(len(pitch[0])):
            if j == 0:
                pass
            else:
                ret[pitch[i][0]] = ret[pitch[i][0]] + pitch[i][j]
    if field != "":
        for i in range(len(field)):
            for j in range(len(field[0])):
                if j == 0:
                    pass
                else:
                    ret[field[i][0]] = ret[field[i][0]] + field[i][j]
    return ret

def dicToLst(d):
    l = []
    for key in d:
        l += [[key, d[key]]]
    return l

def truncate(n):
    n[1] = '%.2f'%(n[1])

def main():
    ''' Runs the boy'''
    # THIS WEEK's STATS
    BATTER_STATS = cleanBatStat(readFiles("Batting.csv", "Batter"))
    #print(B_COLUMN_KEY)
    #print(BATTER_STATS)
    PITCHER_STATS = cleanPitchStat(readFiles("Pitching.csv", "Pitcher"))
    #print(PITCHER_STATS)
    #FIELDER_STATS = cleanPitchStat(readFiles('Fielding.csv', 'Fielder'))
    #print(FIELDER_STATS)
    
    normalize(PITCHER_STATS, 'Pitching')
    normalize(BATTER_STATS, 'Batting')
    #normalize(FIELDER_STATS, 'Fielding')
    
    weekly = dicToLst(calc(BATTER_STATS, PITCHER_STATS))
    # https://stackoverflow.com/questions/18142090/python-sort-a-list-of-lists-by-an-item-in-the-sublist
    # https://stackoverflow.com/questions/8595973/truncate-to-three-decimals-in-python/49845864
    weekly = list(map(lambda x: [x[0], '%.2f'%(x[1])], sorted(weekly, key=operator.itemgetter(1), reverse=True)))
    #print(weekly)

    #SEASON LONG STATS
    BATTER_STATS_O = cleanBatStat(readFiles("BattingS.csv", "Batter"))    
    PITCHER_STATS_O = cleanPitchStat(readFiles("PitchingS.csv", "Pitcher"))    
    FIELDER_STATS_O = cleanPitchStat(readFiles('Fielding.csv', 'Fielder'))
    normalize(PITCHER_STATS_O, 'Pitching')
    normalize(BATTER_STATS_O, 'Batting')
    normalize(FIELDER_STATS_O, 'Fielding')
    year = dicToLst(calc(BATTER_STATS_O, PITCHER_STATS_O, FIELDER_STATS_O))
    year = list(map(lambda x: [x[0], '%.2f'%(x[1])], sorted(year, key=operator.itemgetter(1), reverse=True)))
    #print(year)

    pt = PrettyTable()
    pt.field_names = ["Last Week", "Season"]
    for i in range(len(year)):
        pt.add_row([weekly[i], year[i]])
    print(pt)

    f = open(WEEK + "results.txt", "w")
    f.write(pt.get_string())
    f.close()
main()
