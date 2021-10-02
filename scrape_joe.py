from bs4 import BeautifulSoup
import requests
import pandas as pd
import datefinder # nonstandard
import re
import pytz

with open('joe_full_xml.xml', 'wb') as f:
  req = requests.get("https://www.aeaweb.org/joe/resultset_output.php?mode=full_xml")
  f.write(req.content)
infile = open("joe_full_xml.xml","r")
contents = infile.read()
soup = BeautifulSoup(contents,'lxml')
positions = soup.find_all('position')

reltags = ['jp_section',
           'jp_title',
           'jp_institution',
           'jp_division',
           'jp_department',
           'jp_salary_range',
           'jp_agency_insertion_num',
           'jp_application_deadline']

pattern = r'[Aa]pplication|[Ss]ubmit'

alldat = []
for position in positions:
    row = []
    for tag in reltags:
        try:
            row.append(position.find(tag).text)
        except:
            row.append('')

    # there isn't always a keyword here, but pull it if there is
    try:
        row.append('/'.join(position.find('jp_keywords').text.strip('\n').split('\n')))
    except:
        row.append('')

    # get the dates from the application results.
    description = position.find('jp_full_text').text.replace('\n',' ')
    matches = re.finditer(pattern,description)
    newstrings = []
    for m in matches:
        newstrings.append(description[m.start()-100:m.end()+100])
    description = ' '.join(newstrings)
    if description:
        alldates = []
        matches = list(datefinder.find_dates(description))
        for m in matches:
            if (m.replace(tzinfo=pytz.UTC)>pd.Timestamp('2021-10-05',tzinfo=pytz.UTC)
                and m.replace(tzinfo=pytz.UTC)<pd.Timestamp('2022-03-01',tzinfo=pytz.UTC)):
                alldates.append(m)
        if alldates:
            row.append(min(alldates).strftime('%Y-%m-%d'))
        else:
            row.append('')
    else:
        row.append('')
    alldat.append(row)


out = pd.DataFrame(alldat,columns=['section',
                                   'title',
                                   'institution',
                                   'division',
                                   'department',
                                   'salary_range',
                                   'agency_insertion_num',
                                   'application_deadline',
                                   'keywords',
                                   'description_date'])

out.to_csv('joe_scrape.csv',index=False)
