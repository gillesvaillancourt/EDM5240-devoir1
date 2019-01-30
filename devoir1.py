import datetime, csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from sourcesBachir import lessources
from joueurs import lesjoueurs
from sourcesEureka import eurekaSources

# joueur = input("Quel joueur? ")
# source = input("Quelle source? ")
# # annee = input("Quelle année? ")
debut = input("On commence où? ")

for source in lessources:
	for joueur in lesjoueurs:

		fichier = "extraction-{}-{}.csv".format(lesjoueurs.index(joueur),lessources.index(source))
		print(fichier)
		joueurAvecGuillemets = "\"" + joueur + "\""

		# if mois == "février":
		# 	jours = 28
		# elif mois == "avril" or mois == "juin" or mois == "septembre" or mois == "novembre":
		# 	jours = 30
		# else:
		# 	jours = 31

		yo = webdriver.Firefox()

		yo.get("https://res.banq.qc.ca/login?url=https://nouveau.eureka.cc/access/ip/default.aspx?un=bnat1")
		# print(yo.page_source)

		# for jour in range(1,jours+1):

		print("On va chercher {} dans {}".format(joueur,source))

		try:
			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.ID, "NUM")))
			pseudo = yo.find_element_by_id("NUM")
			pseudo.send_keys("01061722")
			passe = yo.find_element_by_id("PWD")
			passe.send_keys("21854218")
			yo.find_element_by_xpath("//input[@type='submit']").click()
		except:
			print("Prout 1 - À l'identification sur le site BANQ")

		try:
			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "bouton")))
			piton = yo.find_element_by_partial_link_text("accepte")
			piton.click()
		except:
			print("Prout 2 - Au bouton «J'accepte»")

		try:
			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.CLASS_NAME, "lnk-text")))
			acces = yo.find_element_by_link_text("Recherche avancée")
			acces.click()
		except:
			print("Prout 3 - À la première page Eurêka («Recherche avancée»)")

		try:
			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.ID, "Keywords")))
			champ = yo.find_element_by_id("Keywords")
			champ.send_keys(joueurAvecGuillemets)
		except:
			print("Prout 4 - À entrée du nom du joueur")

		try:
			yo.find_element_by_id("specific-sources-rd").click()
			# yo.find_elements_by_css_selector("input[type='radio'][id='specific-sources-rd']").click()
		except:
			print("Prout 5 - Au clic sur bouton 'Nom de source'")

		try:
			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.ID, "sourcesFilter")))
			entrerSource = yo.find_element_by_id("sourcesFilter")
			entrerSource.send_keys(source)

			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.ID, "filterResult")))

			for s in eurekaSources:
				if s[0] == source:
					code = s[1]
			print(source,code)

			element = WebDriverWait(yo,10).until(
				EC.presence_of_element_located((By.ID, code)))
			yo.find_element_by_id(code).click()
		except:
			print("Prout 6 - Au choix de source")

		try:
			rech = yo.find_element_by_class_name("button-search-orange")
			rech.click()
		except:
			print("Prout 7 - Au clic pour déclencher recherche")

		element = WebDriverWait(yo,10).until(
			EC.presence_of_element_located((By.ID, "titleResultList")))
		pageSource = yo.page_source
		page = BeautifulSoup(pageSource,"html.parser")

		nb1 = page.find("div", id="titleResultList").text.strip()
		nb2 = nb1.split("sur")
		nb = int(nb2[1].strip())
		print(nb)

		if nb != 0:
			print("Il y a {} articles sur {} dans {}".format(nb,joueur,source))

			for nbPage in range(int(debut),nb):
				url = "https://nouveau-eureka-cc.res.banq.qc.ca/Search/ResultMobile/" + str(nbPage)
				print(url)
				yo.get(url)
				element = WebDriverWait(yo,10).until(
					EC.presence_of_element_located((By.ID, "docText")))
				source = yo.page_source
				page = BeautifulSoup(source,"html.parser")
				media = page.find("span", class_="DocPublicationName").text.strip()
				mots = page.find("span", class_="DocHeader").text.strip()
				# print(mots)
				mots = mots.split("mots")
				# print(mots)
				mots = mots[0].strip().split(" ")
				# print(mots)
				mots = int(mots[-1].strip())
				# print(mots)
				titre = page.find("div", class_="titreArticle").text.strip()
				try:
					auteur = page.find("div", class_="docAuthors").text.strip()
				except:
					auteur = page.find("div", class_="titreArticle").find_next("div").text.strip()
					if len(auteur) > 150:
						auteur = "Inconnu"
				code = page.find("div", class_="publiC-lblNodoc").text.strip()
				article = [auteur,media,titre,mots,jour,mois,annee,code,nbPage,nb]
				print(article)

				henri = open(fichier, "a")
				bourassa = csv.writer(henri)
				bourassa.writerow(article)

		else:
			print("Il n'y a aucun article sur {} dans {}".format(joueur,source))
