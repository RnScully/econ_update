import pandas as pd
import argparse

def lookup(bases):
    '''
    A helperfunction to produce a pair of dictonaries that associate base codes to base names and back again. 
    +++++++++
    Parameters
    bases (list of dictonaries): a raw read of the marketcommodities.ini as a dictonary

    +++++++++
    Returns
    two dictonaries for fast lookup of name/code relationship. 
    base_code_lookup (dict): keys as names, codes as values
    base_name_lookup (dict): keys as codes, names as values
    '''
    base_code_lookup = {base['Name'].strip('\n').strip(';'): base['base_code'].strip('\n').strip(';').lower() for base in bases}
    base_name_lookup = {v: k for k, v in base_code_lookup.items()}
    return base_code_lookup, base_name_lookup

def find_base_section(base_code, lines):
    ''' a helperfunction which finds the start and end of the section of lines 		relevant to a given base
    +++++++++
    Parameters
    base_code(str): base code formatted from base_code_lookup
    lines(string): list formated read-in of marketcommodities.ini
    +++++++++
    Returns
    start(int): index of start point of the section for the base_code passed in
    end(int): index of endpoint of the section for the base_code passed in. 
    '''

    start = lines.index('base = '+ base_code.lower()+'\n')
    try:
        end = lines[start:].index('[BaseGood]\n')+start
    except ValueError:
        end = len(lines)-1
    return start, end



def parse_goods(goods_path):
    '''
    function to go to the goods ini and come up with the base prices of each commodity. 
    ++++++++++
    Parameters
    goods_path(str): filepath of goods.ini
    ++++++++++
    Returns
    prices(dct): 
    '''
    with open(goods_path) as fp: #open goods file
        Lines = fp.readlines() 
        prices = dict()

        for lines in Lines: #pull out the commodity name and price from each entry. 
            if lines[:8] == 'nickname':
                nick = lines[11:].strip('\n')
            if lines[:8] == 'price = ':
                price = lines[8:].strip('\n')
                prices[nick] = int(price) 
    return prices

def get_data(comm_markets_path, distances_path):
    '''
    A function that pulls in the data from marketcommodities.ini and the flc dump file and scrapes it. 
    +++++++++
    Parameters:
    comm_markets_path (str): the path of market_commodities.ini
    distances_path (str): the path of the flc dump file
    +++++++++
    Returns
    distances (Dataframe): pandas dataframe of all the viable distances between bases
    bases(list of dictonaries): list containing all of the base entries in market_commodities.ini in dictonary 
    form. Dictonaies hold base_code, base_name, and list of commodities traded. 
    comm_set (set): set of all commodities bought or sold on all bases
    base_names (list): all base names
    '''


    distances = pd.read_csv(distances_path, names = ['start', 'end', 'time'])
    distances = distances[distances['start']!=distances['end']]
    distances = distances[distances['time']!=-1]

    with open(comm_markets_path, 'r') as file:
        lines = file.readlines() 
    
    comment_count = 0
    bases = []
    commodities =[]
    for i in lines[2:]:
        if i.lower() == '[basegood]\n' or i == ';EVERYTHING BELOW THIS LINE IS DATABASE.': #there's a better way to parse the end of file in the generate multiples function. 
            if comment =='':
                comment = base_code
            bases.append({'base_code':base_code, 'Name':comment, 'commodities':commodities})
            commodities=[]
            comment = ''
            comment_count = 0
        if i[:4].lower() == "base":
            base_code = i[7:]
        if i[:1] == ';' and comment_count == 0:
            comment = i
            comment_count+=1
        elif i[:1]==';':
            
            comment +'\n'+ i
        if i[:10].lower() == 'marketgood':
            t =i[13:].split()
            l = [float(j.strip(',')) for j in t[1:6]]
            l.append(float(t.pop()))
            l.append(t[0])
            commodities.append(l)
    
    comm_set = set([])
    for i in bases: #this loop in loop adds all the commodities to a set so we know how many commodities to display in our applet
        j = i['commodities']
        for k in j:
            comm_set.add(k[6])
    base_names=[(base['Name'],base['base_code']) for base in bases]
    
    return distances, bases, comm_set, base_names


def generate_multiple(lines, base_price, end_code, start_code, crsec, commodity, secs):
    '''
    Function which generates the price multiple for marketcommodities.ini, 
    and finds the location in market_commodities.ini that is going to be replaced. 
    Parameters
    +++++++++
    lines(lst): list formated read-in of marketcommodities.ini
    base_price(int): base price of the good from goods.ini
    end_code(str): base code of the base where the trade route ends.
    start_code(str): base code of the base where the trade route starts.
    crsec(int): profits per second that he route should make
    commodity(str): commodity code of the relevant commodity #why is commodity needed here?!?!
    secs(int): time in seconds that the route takes. 
    +++++++++
    Returns:
    multiple(float): intended_price/base_price, the buy price divided by base to generate the multiple the game needs
    buyingval(int): string that is the relevant line in market_commodities.ini that will be updated and replaced. 
    buingidx(int): index in lines of the entry of the buying base. 
    
    '''
    # finds the section in market_commodities relevant to the buying base. 
    start, end = find_base_section(end_code, lines)

    for line in lines[start: end]: #then finds the specific line relevant to the commodity in question
        if commodity in line:
            buyingidx = lines.index(line)
            buyingval = line

    #finds the section in market_commodities relevant to the selling base
    start, end = find_base_section(start_code, lines)
    
    for line in lines[start: end]: #then finds the specific line relevant to the commodity in question
        if commodity in line:
            sellingidx = lines.index(line)
            sellingval = line

    sellprice = base_price * float(sellingval.split().pop()) #generate actuall price the start of route sells at. 
    #construct multiple from secs*crsec + base
    intended_price = (secs*crsec/100)+sellprice
    return intended_price/base_price, buyingval, buyingidx

def update_lines(commodity, start_base, end_base, lines, crsec):
    '''
    will update the multiple of the endpoint of the route at the right commodity in lines. 
    ++++++++++
    Parameters
    commodity(str): commodity code of the relevant commodity
    end_code(str): base code of the base where the trade route ends.
    start_code(str): base code of the base where the trade route starts.
    lines(lst): list formated read-in of marketcommodities.ini
    crsec(int): profits per second that he route should make
    ++++++++++
    Returns
    lines(list): market_commodities.ini representation with updated thing. 
    '''
    #lookup the codes for distances
    end_code = base_code_lookup[end_base]
    start_code = base_code_lookup[start_base]

    #dig up the time between bases and format it to seconds. 
    time =distances[(distances['end'] == end_code.lower()) & (distances['start'] == start_code.lower())]['time']
    secs =int(time)/1000 + 20 # +20 becuase it takes time to undock that flcomp doesn't know about.
    base_price = prices[commodity]
    multiple, buyingval, buyingidx = generate_multiple(lines, base_price, end_code, start_code, crsec, commodity, secs)


    buy = buyingval.split()
    buy[8]= str(multiple)
    lines[buyingidx]=' '.join(buy)
    return lines

def write_market(lines):
    '''
    writes the market_commodities.ini lines to a file. 
    ++++++++++
    Parameters
    lines(lst): market_commodities.ini stored as list of strings, a sring for each line of the file. 
    '''
    with open('new_market.ini', 'w') as f:
        for item in lines:
            f.write("%s" % item)
        
def update_from_changes(changes, lines):
    '''
    function that opens from Changes file and applies the changes listed. 
    +++++++++
    Parameters
    changes_path(str): path to the Econ_changes.txt config file
    lines(lst): marketcommodities file turned into lines.
    +++++++++
    Returns
    lines(lst): updated marketcommodities as lines.  
    '''
    #read from changes needed doc
    

    #roll throuhg the changes and apply them    
    for entries in changes:
        item = entries.split(',') 
        commodity = item[2].lstrip()
        start_base = item[0].lstrip()
        end_base = item[1].lstrip()
        crsec = int(item[3])

        lines = update_lines(commodity, start_base, end_base, lines, crsec)

    return lines

def check_for_sell_points(changes, distances, base_code_lookup):
    '''
    finds all the bases in lines that sell the base, and append the travel time to them, 
    to make sure there isn't a better route than the one being suggested. 
    Marketgood = commodity, 0, 0, 150, 500, 0, multiple\n denotes a commodity that sells. 
    ++++++++
    Parameters
    Changes: config file of changes needed
    distances: pandas dataframe of base to base travel times. 
    +++++++
    Returns
    changes, config file trimmed of the in-error requests
    errors: list of bases that have closer than expected routes. 
    '''
    report = []
    for line in changes:
        bases_that_sell = []
        entries = line.split(',')
        commodity = entries[2] #get the commodity in question from changes. 
        endpoint = entries[1].lstrip() 
        endpoint = base_code_lookup[endpoint].lower()#format endpoint for distances

        start_base = base_code_lookup[entries[0]].lower()
        
        
        selling_base_codes = [code.split(' ')[2].strip('\n').lower() for code in bases_that_sell] #format the bases_that_sell for distances

        string = 'Marketgood ='+commodity+', 0, -1, 150, 500, 0,' #format a line so that it matches the lines that sell
        selling_idx = [count for count, value in enumerate(lines) if string in value] #find the location of all the selling lines.
        base_good_idx = [count for count, value in enumerate(lines) if 'BaseGood' in value] #the places each entry of market_commodities starts

        for salepoint in selling_idx:
            for idx in base_good_idx:
                if salepoint-idx < 0:
                    break
                nameidx = idx
                #find closest(and lowest) value in base_good_idx that matches X
            bases_that_sell.append(lines[nameidx+1])
        
        selling_base_codes = [code.split(' ')[2].strip('\n').lower() for code in bases_that_sell] #format the bases_that_sell for distances

        if start_base not in selling_base_codes:
            report.append(base_name_lookup[start_base.lower()]+' inserted as a producer of'+commodity+' at multiple 1')
            
        
        mask = distances[distances['end']==endpoint] #get just the bases in distances that end at the endpoint base
        short = mask[mask['start'].isin(selling_base_codes)] #sort out any base not in selling_base_codes in the start column. 
        start_base = base_code_lookup[changes[0].split(',')[0]].lower()
        closest = short.min()['start']

        
        
        if closest != start_base:
            report.append(line + ' is not the shortest path, '+str(closest)+ ' is closer to'+ endpoint.capitalize())

    return changes, report



def insert_sellpoint(lines, errors):
    '''
    A helperfunction which will parse errors for bases that need a sellpoint and insert them. 
    Puts the new one at the top of the relevant base section, raises an error if the base listed is not in market commodities
    +++++++++
    Parameters
    lines(lst): list formated read-in of marketcommodities.ini
    base_code(str): base code formatted from base_code_lookup
    commodity(str): 
    +++++++++
    Returns
    Lines(lst) list formated read-in of marketcommodities.ini with a new sell point
    '''
    insertions = [string for string in errors if 'inserted' in string]
             
    for string in insertions:
        base_idx = string.find(' inserted')
        commodity_start = base_idx+27
        commodity_end = string.find(' at multiple')

        base_code = base_code_lookup[string[0:base_idx]]
        commodity = string[commodity_start:commodity_end]

        try:
            start, end = find_base_section(base_code, lines)
            marketgood_line = 'Marketgood = '+commodity+', 0, -1, 150, 500, 0, 1\n'
            lines.insert(start+2, marketgood_line)

        except ValueError:
            print(base_code+' is not in market commodities')
            continue
    return lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A tutorial of argparse!')
    parser.add_argument("-cc", default =False, help='(bool) checks whether update_econ is being triggered by the clickable')
    args = parser.parse_args()
    
    clickabled = bool(args.cc) #the bat will pass -cc True in, and needs different directions than running it in folder. 
    

    if clickabled == True: #build out handling for passing in the correct location of things
        path_markets = 'src/market_commodities.ini'
        distances_path = 'src/dump.csv'
        path_goods = 'src/goods.ini'
        config = 'src/Econ_changes.txt'
    else:
        path_markets = 'market_commodities.ini'
        distances_path = 'dump.csv'
        path_goods = 'goods.ini'
        config = 'Econ_changes.txt'
            
    
    #load data from game files and flcompanion output. 
    distances, bases, comm_set, base_names = get_data(path_markets, distances_path)
    base_code_lookup, base_name_lookup = lookup(bases)
    prices = parse_goods(path_goods)

    #open market_commodities
    with open(path_markets) as file:
        lines = file.readlines()
    #run through the Econ_changes.txt file and apply those changes
    with open(config) as template:
        changes = template.readlines()
    changes, errors = check_for_sell_points(changes, distances, base_code_lookup)
    lines = insert_sellpoint(lines, errors)
    update_from_changes(changes, lines)
    for line in errors:
        print(line)
    write_market(lines)
