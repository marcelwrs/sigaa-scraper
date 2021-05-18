# -*- coding: utf-8 -*-
"""
Created on Tue May 18 09:33:10 2021

@author: marcel
"""
from optparse import OptionParser
from mechanize import Browser
from getpass import getpass

# main function
def main():

    # parse command line args
    parser = OptionParser()
    parser.add_option("-u", "--url", type="string", dest="url", default="https://sigaa.ufrrj.br/", help="url de acesso ao sistema de juiz da maratona")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="imprimir mensagens de debug")
    (opt, args) = parser.parse_args()

    # start session
    br = Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # login sigaa
    br.open("https://sigaa.ufrrj.br/sigaa/verTelaLogin.do")
    #br.open("http://google.com")
    br.select_form('loginForm')
    br.form['user.login'] = input("username: ")
    br.form['user.senha'] = getpass("password: ")
    br.submit()
    
    # Open example page 
    br.follow_link(text='Ver turmas anteriores')
    
    # Print previous classes
    for l in br.links():
        if l.text != "" : print(l.text)
   
    return

if __name__ == "__main__":
    main()