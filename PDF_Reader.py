

#%%
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 13:37:41 2024

@author: wfloyd
Writing code to read pdf's into a document.  For this first portion we're
in luck because the pdf's are highly standardized and output from some software, so it's not like a scanned document.
I'm hoping this will be very straightforward because of this.

Update: Everything appears to be working
"""

import pdfplumber
import pandas as pd
from datetime import datetime
import time
import io

#extract_tables(file_path)

def extract_pdf(filepath):
    #Apparently pdf plumber accepts either filepaths or files, so I can pass a pdf file object!
    a = pdfplumber.open(filepath) #PDF object
    return a

def extract_table_from_file(pdf_object,page_number):
    #This function will take in the pdf and page number and give us the relevant info
    b = pdf_object.pages[page_number] #page object

    #extract the tables.  In our case this gives 3 tables, but 2 and 3 are useless.  1 is essentially the whole document
    #and puts each row of the document into its own row.  even the blank rows are just rull "None" rows.  I believe
    #this is exactly what we needed
    c = b.extract_tables()
    return c[0]


def get_relevant_metrics(report_type):
    #All of the metrics have slightly different names in the different reports.  This will help determine the appropriate
    #metric names for the given report

    #There will be some sort of case statement here.  This is for the main signalled report that Dave provided
    if report_type == 'signalized':
        metrics_of_interest = {
            'Delay' : 'Control Delay ( d), s/veh',
            'LOS' : 'Level of Service (LOS)',
            'V/C':'Volume-to-Capacity Ratio ( X)',
            'Int Delay':'Intersection Delay, s/veh / LOS'
            }


    elif report_type == 'two way stop':
        metrics_of_interest = {
            'Delay' : 'Control Delay (s/veh)',
            'LOS' : 'Level of Service (LOS)',
            'V/C':'v/c Ratio',
            'Int Delay':'Intersection Delay, s/veh / LOS'
            }

    #Annoyingly all way stops don't include v/c ratio, we have to calculate it ourselves.
    elif report_type == 'all way stop':
        metrics_of_interest = {
            'Delay' : 'Control Delay (s/veh)',
            'LOS' : 'Level of Service, LOS',
            'v': 'Flow Rate, v (veh/h)',
            'c':'Capacity (veh/h)',
            'V/C':'v/c Ratio',
            'Int Delay':'Intersection Delay (s/veh) | LOS'
            }

    #This is the roundabout case
    else:
        metrics_of_interest = {
            'Delay' : 'Lane Control Delay (d), s/veh',
            'LOS' : 'Lane LOS',
            'V/C':'v/c Ratio (x)',
            'Int Delay':'Intersection Delay, s/veh | LOS'
            }

    return metrics_of_interest


def get_identity_info(report_type):
    #All of the metrics have slightly different names in the different reports.  This will help determine the appropriate
    #metric names for the given report

    #There will be some sort of case statement here.  This is for the main signalled report that Dave provided
    if report_type == 'signalized':
        column_names = ['Project Description','Analysis Year','Time Period']

    #It looks like all the other reports use the same naming convention
    else:
        column_names = ['Project Description','Analysis Year','Time Analyzed']

    return column_names


def get_vc_array(v,c):
    #This is the function that gets the v/c array from the constituent v and c vectors.
    ans = []
    for i in range(len(v)): #This could potentially be a problem but let's hope it isn't
        if v[i] == '':
            ans.append('')
        else:
            num = float(v[i])/float(c[i])
            ans.append(round(num,2)) #These floats have like 10 decimals and it looks awful in here
    return ans


def determine_file_type(pdf_page):
    '''
    We should be able to determine the type of report based on attributes of the pdf.  As a reminder here are the possible reports
    Signalized (there's a single page and full report, but let's just stick with single page for now)
    Unsignalized - Two Way Stop
    Unsignalized - All Way Stop
    Roundabout - Single Lane
    Roundabout - Multi Lane

    and here are the corresponding names I've given them
    signalized
    two way stop
    all way stop
    roundabout sl
    roundabout ml
    '''
    #Recall that the pdf page is an array of arrays.  As luck would have it, item [0][0] always contains info about the name
    #Also worth mentioning that there's no practical difference between single lane and multilane roundabout reports.  I can't
    #find any info in the report that differentiates them other than the image at the top, so I'll just default to a multi lane
    report_title = pdf_page[0][0]
    if  'Signalized' in report_title:
        return 'signalized'
    elif 'Two-Way' in report_title:
        return 'two way stop'
    elif 'All-Way' in report_title:
        return 'all way stop'
    elif 'Roundabouts' in report_title:
        return 'roundabout sl' #As mentioned above just going to return sl.  Don't believe it makes a difference
    return 'Report type not determined'


    return 1


def get_clean_info(table):
    #this is going to take the table that the above spits out and give us the clean data

    report_type = determine_file_type(table)
    if report_type == 'Report type not determined':
        print("Error, report type not determined")
        return
    metrics_of_interest = get_relevant_metrics(report_type)


    #Alright the above metrics are what we're interested in.  We're going to loop through and find the rows in the
    #extracted table that begin with those metrics
    to_return = {}


    #We also want some identifying info for the data we're pulling here.  We definitely want the
    #AM or PM info, but also the projection description and year.
    #Now I'm not 100% sure how standardized the header is going to be in these reports,  and if weird
    #stuff can happen like things get pushed to the next line.  We're going to
    #search row by row looking for our data.  Can't just assume its the first element in the row

    identifying_info = get_identity_info(report_type)

    going_into_table = []
    for field in identifying_info:
        #loop through the rows
        for row in table:
            clean_row = [j for j in row if j != None] #strip out the Nones
            for i in range(len(clean_row)):
                if clean_row[i] == field: #this means we've got a hit
                    #print(clean_row[i],clean_row[i+1]) #The data we want will be one column to the right
                    going_into_table.append(clean_row[i+1])

                    break

    #we need the extra brackets here so it becomes a row, not a column
    to_join = pd.DataFrame([going_into_table])

    #This begins where we get the data
    for metric in metrics_of_interest.keys():

        name_in_pdf = metrics_of_interest[metric] #the row we want begins with this name
        for i in table: #I don't know if these will always be in the same order so we'll do it the old fashioned way
            #print(i)
            if i[0] == name_in_pdf:
                #A lot of the padding and stuff comes in as none types.  Now thankfully blanks do not!
                #By removing the None's all that's left is the data
                clean_row = [j for j in i if j != None]

                if metric != 'Int Delay': #Int Delay needs to be handled a bit differently since we tack it on to the right of the table
                    to_return[metric] = clean_row[1:] #drop the name

                else: #This means it's Int Delay and needs to be added to the right side of the table
                    int_delay = clean_row[1:]
                break

    #When it's an all way stop we have to manually calculate the v/c ratio.  The v and c were brough in so it won't be too tough
    #
    if report_type == 'all way stop':
        #pull in the v and c values
        vs,cs = to_return['v'],to_return['c']
        vc = get_vc_array(vs,cs) #calculate the ratios
        to_return['V/C'] = vc
        #Now we have to remove the v and c rows
        del to_return['c']
        del to_return['v']
    elif report_type == 'two way stop':
        #report type two way stop does not have an int delay? So we'll make a dummy one here
        int_delay = ['','']

    data_from_pdf = pd.DataFrame.from_dict(to_return,orient='index').reset_index()
    data_from_pdf = data_from_pdf.rename(columns={'index':'Metric'})
    #Now we tack on the int_delay info.  Need the placeholder to get it to three rows
    data_from_pdf['Int Delay'] = int_delay + ['']


    #Rename the columns.  This is arguably a bit manual but I'm not sweating it for now.  If I shuffle
    #the column order I'll have to change it here
    broadcasted_single_row_df  = pd.concat([to_join] * len(data_from_pdf), ignore_index=True).rename(columns={0:'Time',1:'Year',2:'Project'})
    result = pd.concat([broadcasted_single_row_df, data_from_pdf], axis=1)
    return result



def create_excel_file(file_path,pandas_table):

    # Write the DataFrame to an Excel file
    pandas_table.to_excel(file_path, sheet_name = 'Page One', index=False)




def generate_random_string(length):
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string



def write_to_excel(workbook_path,page_name,data):
      # Load the existing workbook
      # To my knowledge the workbook must already exist, it doesn't make a new one
    with pd.ExcelWriter(workbook_path, mode='a', engine='openpyxl') as writer:

        if page_name in writer.book.sheetnames:
            writer.book.remove(writer.book[page_name])

        # Write the DataFrame to the existing workbook
        data.to_excel(writer, sheet_name=page_name, index=False)


def get_time_string():
    #Want to name the files something different
    current_datetime = datetime.now()

    year = str(current_datetime.year)
    month = str(current_datetime.month)
    day = str(current_datetime.day)
    #hour = current_datetime.hour
    #minute = current_datetime.minute
    second = str(current_datetime.second)

    #Pad with lead zero
    month,day = '0'+month,'0'+day
    month,day = month[-2:],day[-2:]
    print(year,month,day)
    ans = year +"_"+month+"_"+day+"_"+second
    return ans


#Apparently for website apps we need to write directly to memory, so we can
#do that like this:
def write_excel_file(pandas_df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        pandas_df.to_excel(writer, index=False)
    output.seek(0)  # move pointer to start of file

    return output.getvalue()  # returns bytes

#def call_everything(pdf_path,excel_path_prefix):
def call_everything(pdf_path):
    #Pull in the pdf
    #reminder this can be a file according to chatgpt.
    main_pdf = extract_pdf(pdf_path)



    #Get the pages
    my_pages = main_pdf.pages


    #Create the skeleton that will hold all the data
    final_table = pd.DataFrame()


    for page in range(len(my_pages)):
        print(f"reading page {page}")
        main_table = extract_table_from_file(main_pdf,page) #will need to loop through all pages at somepoint
        x = get_clean_info(main_table)

        #Append data to the final table
        final_table = pd.concat([final_table, x], ignore_index=True)
        report_type = determine_file_type(main_table) #We want the report type in the excel name imo

    if report_type == 'roundabout sl':
        report_type = 'roundabout'  #due to the previously mentioned fact that sl and ml are identical


    print("Pandas dataframe created")

    time.sleep(1) #Do this so there's no clashing in the names which only go to the second\

    #adding a random alphanumeric string of length 5 to make sure no clashing in naming conventions.
    random_string = "_" + generate_random_string(5)
    #tab_name = get_time_string() +"_"+ report_type + random_string
    #excel_path = excel_path_prefix + f'\{tab_name}.xlsx'
    #print(f"putting data in {excel_path}")

    # Usage example:
    #create_excel_file(excel_path,final_table)
    #This should handle it
    excel_bytes = write_excel_file(final_table)
    return excel_bytes



