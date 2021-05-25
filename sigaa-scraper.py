# -*- coding: utf-8 -*-
"""
Created on Tue May 18 09:33:10 2021

@author: marcel
"""
from optparse import OptionParser
from getpass import getpass
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
import time
import os
import pickle

oldcurr = "00326"
newcurr = "00356"
currtext = {oldcurr: "2016.1", newcurr: '2020.1'}
currl = [oldcurr, newcurr]
curriculum = {}

def dologin(opt, driver):
    # login sigaa
    driver.get(opt.url + "/sigaa/verTelaLogin.do")
    #assert "Python" in driver.title
    elem = driver.find_element_by_name("user.login")
    elem.send_keys(opt.username)
    elem = driver.find_element_by_name("user.senha")
    elem.send_keys(opt.password)
    elem.send_keys(Keys.RETURN)
    time.sleep(3)
    if (driver.page_source.count("rio e/ou senha inv") == 0):
        return True
    else:
        return False
    return True


def getcomponents(opt, driver):
    actions = ActionChains(driver)
    
    elem = driver.find_element_by_id("ensino")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("ensino_Consultas")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("menu:ensCons_OrientacaoAtividades")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("ensCons_Estrutura")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("menu:ensConsTec_Estrutura")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("menu:ensConsGrad_Estrutura")
    actions.move_to_element(elem)    
    actions.click(elem)
    actions.perform()
    time.sleep(3)
    
    actions = ActionChains(driver)
    elem = driver.find_element_by_id("busca:checkCurso")
    actions.move_to_element(elem)
    actions.click(elem)
    actions.perform()
    
    elem = driver.find_element_by_id("busca:curso")
    drop = Select(elem)
    drop.select_by_value("450642")

    #actions = ActionChains(driver)
    #elem = driver.find_element_by_id("busca:checkCurso")
    #actions.move_to_element(elem)
    #actions.click(elem)
    #actions.perform()

    time.sleep(1)

    elem = driver.find_element_by_xpath('//*[@id="busca"]/table/tfoot/tr/td/input[1]')
    elem.send_keys(Keys.RETURN)
    
    time.sleep(2)
    
    content = driver.page_source
    soup = BS(content, 'html5lib')
    rows = [tr.findAll('td') for tr in soup.find_all('tr', {"class": ["linhaPar", "linhaImpar"]})]

    curriculum = {}
    for r in rows:
        for currid in currl:
            if str(r[0]).count(currid) == 1:
                curriculum[currid] = {}
                
                elemid = r[4].find("a").get("id") #ID
                elem = driver.find_element_by_id(elemid)
                elem.send_keys(Keys.RETURN)
                time.sleep(2)
    
                content = driver.page_source
                soup = BS(content, 'html5lib')
                comps = [tr.findAll('td') for tr in soup.find_all('tr', {"class": "componentes"})]
                for comp in comps:
                    code = str(comp[0].text).strip()
                    curriculum[currid][code] = {}
                    curriculum[currid][code]['name'] = str(comp[1].text).strip()
                    curriculum[currid][code]['type'] = str(comp[3].text).strip()
                    curriculum[currid][code]['nature'] = str(comp[4].text).strip()
                    
                driver.execute_script("window.history.go(-1)")
                time.sleep(2)
          
    #time.sleep(10)
    
    return curriculum


def addpreeq(opt, driver, curriculum):
    driver.get(opt.url + "/sigaa/verPortalDocente.do")
    time.sleep(2)
    actions = ActionChains(driver)
    
    elem = driver.find_element_by_id("ensino")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("ensino_Consultas")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("menu:ensCons_OrientacaoAtividades")
    actions.move_to_element(elem)    
    elem = driver.find_element_by_id("menu:ensConsGrad_Disciplinas")
    actions.move_to_element(elem)    
    actions.click(elem)
    actions.perform()
    time.sleep(2)
    
    # for each comp in components
    for curr in currl:
        for comp in curriculum[curr].keys():

            elem = driver.find_element_by_xpath('//*[@id="formBusca"]/table/tbody/tr[2]/td[3]/input')
            elem.clear()
            elem.send_keys(comp)
            elem = driver.find_element_by_id("formBusca:btnBuscar")
            elem.send_keys(Keys.RETURN)
            time.sleep(2)
            
            content = driver.page_source
            soup = BS(content, 'html5lib')
            rows = [tr.findAll('td') for tr in soup.find_all('tr', {"class": ["linhaPar", "linhaImpar"]})]
        
            elemtitle = rows[0][6].find("a").get("title")
            elem = driver.find_element_by_xpath('//*[@title="' + elemtitle + '"]')
            elem.send_keys(Keys.RETURN)
            time.sleep(2)
        
            content = driver.page_source
            soup = BS(content, 'html5lib')
            rows = [tr.findAll('td') for tr in soup.find_all('tr', {"class": ["linhaPar", "linhaImpar"]})]
            
            curriculum[curr][comp]["pre"] = []
            curriculum[curr][comp]["eq"] = []
            for row in rows:
                if len(row) == 5:
                    # prerequisite
                    if (row[2].text.count("Requisito") == 1) and (row[3].text.count(currtext[curr]) == 1):
                        curriculum[curr][comp]["pre"].append(row[1].text)
                    # equivalency
                    if row[2].text.count(curr) == 1:
                        curriculum[curr][comp]["eq"].append(row[0].text)
                if len(row) == 6:
                    # semester
                    if row[0].text.count(curr) == 1:
                        curriculum[curr][comp]["sem"] = row[4].text
                    
            driver.execute_script("window.history.go(-1)")
            time.sleep(2)
    return

# main function
def main():

    # parse command line args
    parser = OptionParser()
    parser.add_option("-l", "--url", type="string", dest="url", default="https://sigaa.ufrrj.br", help="sigaa server URL (without trailing backslash)")
    parser.add_option("-d", "--datadir", type="string", dest="datadir", default="data", help="directory to store data")
    #parser.add_option("-u", "--user", type="string", dest="username", help="sigaa username")
    #parser.add_option("-p", "--pass", type="string", dest="password", help="sigaa password")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="print debug messages")
    (opt, args) = parser.parse_args()

    dirpath = os.path.join(os.getcwd(), opt.datadir)
    if not os.path.exists(dirpath):
        print("Creating data dir.")
        os.mkdir(dirpath)

    userinfo = os.path.join(os.getcwd(), opt.datadir, "userinfo.pickle")
    if os.path.exists(userinfo):
        print("Reading credentials from file.")
        file = open(userinfo, 'rb')
        data = pickle.load(file)
        file.close()
        opt.username = data['username']
        opt.password = data['password']
    else:
        print("Please, inform SIGAA credentials.")
        opt.username = input("Username: ")
        opt.password = getpass("Password: ")
        file = open(userinfo, 'wb')
        pickle.dump({'username': opt.username, "password": opt.password}, file)
        file.close()
        
    datafile = os.path.join(os.getcwd(), opt.datadir, "curriculum.pickle")
    if os.path.exists(datafile):
        print("Reading curriculum from file.")
        file = open(datafile, 'rb')
        data = pickle.load(file)
        file.close()
        curriculum = data['curr']
    else:
        # start session
        driver = webdriver.Firefox()
    
        # login
        while not dologin(opt, driver):
            print("Usuário e/ou senha inválidos!")
    
        # get componentes curriculares
        curriculum = getcomponents(opt, driver)
        #print(curriculum)
    
        # get prerequisites
        addpreeq(opt, driver, curriculum)

        file = open(datafile, 'wb')
        pickle.dump({'curr': curriculum}, file)
        file.close()
        driver.close()

    # print all components with prerequisite for each curriculum
    for curr in curriculum.keys():
        print ("Grade: " + currtext[curr])
        for comp in curriculum[curr]:
            if len(curriculum[curr][comp]["pre"]) > 0:
                print("\tDisciplina: " + comp + "-" + curriculum[curr][comp]["name"])
                print("\t\tTipo: " + curriculum[curr][comp]["type"])
                print("\t\tNatureza: " + curriculum[curr][comp]["nature"])
                print("\t\tPre-requisitos: " + str(curriculum[curr][comp]["pre"]))
                print("\t\tEquivalencias: " + str(curriculum[curr][comp]["eq"]))
    #print(curriculum)

    return

if __name__ == "__main__":
    main()