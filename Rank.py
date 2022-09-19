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
####### OFFENSE ############
# 0-Team Name | PA | Runs | Stolen Bases | BB% | 5- K% | ISO | BABIP | AVG | OBP | 10- SLG | wOBA | wRC+ | BaseRuns| OSwing | ZContact | HardHit
####### PITCHING ###########
# 0- Team Name | IP | k/9 | bb/9 | hr/9 | 5- BABIP | LOB% | ERA | FIP | xFIP | 10- WHIP

bcols = [0, 1, 2, 4, 5, 9, 10, 13, 14, 15, 16]
bcolv = ['Team Name', 'Runs/PA', 'BB%', 'K%', 'OPS', 'BsR', 'OSwing%', 'ZCon%', 'HH%']
pcols = [0, 2, 3, 4, 7, 8, 10]
pcolv = ['K/9', 'BB/9', 'HR/9', 'FIP', 'WAR']
fcols = [0, 10, 23]
fcolv = ['DRS', 'DEF']
WEEK = "./24/" # CHANGE THIS TO GET PROPER FILENAMES
#PATH = // maybe useful for the future


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
    # cols is the columns of OBP and SLG, should always be adjacent because of list concatenation
    OPS = teamStats[cols[0]] + teamStats[cols[1]]
    return teamStats[:cols[0]] + [OPS] + teamStats[cols[1] + 1:]

def calcRPA(teamStats, cols):
    '''Calculate Runs per PA'''
    # cols is the columns of PA and R, should always be adjacent because of list concatenation
    RPA = float(teamStats[cols[1]]) / float(teamStats[cols[0]])
    return teamStats[:cols[0]] + [RPA] + teamStats[cols[1] + 1:]     


def trimPct(teamStats, cols):
    '''Remove the space and PCT sign at the end of stats that need it'''
    temp = []
    for i in range(len(teamStats)):
        if i in cols:
            teamStats[i] = teamStats[i][:-1]
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
        # give all cols with %s in trimpct (indexes are/refer to bcols, not the overall list, it's confusing), then OBP and SLG 
        cleaned += [calcRPA(calcOPS(trimPct(team, [3, 4, 8, 9, 10]), [5, 6]), [1, 2])]
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

def minBest(stats, index, hi, lo, nhi=10, nlo=0):
    '''calculates adjusted points out of of 10 where smallest is best'''
    for j in range(len(stats)):
        stats[j][index] = 10- ((((stats[j][index] - lo) / (hi-lo)) * (nhi-nlo))+nlo )
        #stats[j][index] = 10 - ((stats[j][index] * 10) / rang)
        
def maxBest(stats, index, hi, lo, nhi=10, nlo=0):
    '''calculates adjusted points out of of 10 where largest is best'''
    for j in range(len(stats)):
        temp = stats[j][index]
        #print((stats[j][index] - lo) / (hi-lo))
        stats[j][index] = (((stats[j][index] - lo) / (hi-lo)) * (nhi-nlo))+nlo 
        #stats[j][index] = (stats[j][index] * 10) / rang
        if stats[j][index] < 0 or stats[j][index] > 10:
            pass
            #print( "values " + str(temp) + " did not map in " + str(hi) + " & " + str(lo) + ", instead to " + str(stats[j][index]))
            
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
            #go again now that none are negative
            high, low = findMinMax(stats, i)
            if low < 0:
                print("idioot")
            #for j in range(len(stats)):
            # if you want to change the stats involved you have to adjust these
            # should be: RPA, BB%, OPS, BsR, ZCon, HH & k/9
            if (statType == 'Batting' and i in [1, 2, 4, 5, 7, 8]) or \
                (statType == 'Pitching' and i in [1]) or \
                statType == 'Fielding':
                #print('here')
                maxBest(stats, i, high, low)
            else:
                #print('here2')
                minBest(stats, i, high, low)


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
    #FIELDER_STATS_O = cleanPitchStat(readFiles('Fielding.csv', 'Fielder'))
    normalize(PITCHER_STATS_O, 'Pitching')
    normalize(BATTER_STATS_O, 'Batting')
    #normalize(FIELDER_STATS_O, 'Fielding')
    year = dicToLst(calc(BATTER_STATS_O, PITCHER_STATS_O))
    year = list(map(lambda x: [x[0], '%.2f'%(x[1])], sorted(year, key=operator.itemgetter(1), reverse=True)))
    #print(year)

    # "Team Name" , "RPA" ,  "BB%" , "K%" , "OPS" ,  "BaseRuns", "OSwing" , "ZContact" , "HardHit"
    pto = PrettyTable()
    pto.field_names = ["Team Name" , "RPA" ,  "BB%" , "K%" ,  "OPS" , "BSR", "OSwing" , "ZContact" , "HardHit"]
    for i in range(len(BATTER_STATS)):
        pto.add_row(BATTER_STATS[i])
    #print(pto)
    
    pt = PrettyTable()
    pt.field_names = ["Last Week", "Season"]
    for i in range(len(year)):
        pt.add_row([weekly[i], year[i]])
    print(pt)

    f = open(WEEK + "results.txt", "w")
    f.write(pt.get_string())
    f.close()
main()
