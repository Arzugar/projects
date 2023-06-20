#!/usr/bin/python3.8

import requests
from bs4 import BeautifulSoup
import urllib.parse
import click


# Fonction de recherche
def recherche_annuaire (search='', pros=False, num=False):
	if pros:
		if num:
			url = r"http://www.cheznoo.net/annuaire/home/index_pros.php?s_activite=&s_numero="+urllib.parse.quote(search)+"&s_adresse=&s_ville=&submit.x=0&submit.y=0&a=search"

		else:
			url = r"http://www.cheznoo.net/annuaire/home/index_pros.php?s_activite="+urllib.parse.quote(search)+"&s_numero=&s_adresse=&s_ville=&submit.x=0&submit.y=0&a=search"

		f = 'r-pro-block'


	else:
		if num:
			url = r"http://www.cheznoo.net/annuaire/home/index.php?s_nom=&s_numero="+urllib.parse.quote(search)+"&s_adresse=&s_ville=&submit.x=0&submit.y=0&a=search"
		else:
			url = r"http://www.cheznoo.net/annuaire/home/index.php?s_nom="+urllib.parse.quote(search)+"&s_numero=&s_adresse=&s_ville=&submit.x=0&submit.y=0&a=search"
		f = 'r-abo-block'
	
	r = requests.Session().get(url)
	soup= BeautifulSoup(r.text,'lxml')

	abonnes = soup.find_all('div',f)

	data = []
	for abo in abonnes:
		nom = abo.find('div', 'abo-nom').text
		adresse = ' '.join([a.text for a in abo.find_all('div','abo-adresse')])
		nums = [(n.find('div','abo-num-label').text,n.find('div','abo-num-digits').text) for n in abo.find_all('div','abo-num')]
		data.append((nom,adresse,nums))
	return data


@click.command()
@click.option('-p', '--pros',is_flag=True, help='[Flag] Rechercher parmis les professionels')
@click.option('-n','--num', is_flag=True,help='[Flag] Recherche par numero')
@click.argument('recherche',type=str)
def main(pros, num, recherche):
	"""Annuaire qui cherche sur https://cheznoo.net"""
	result = recherche_annuaire(recherche, pros, num)
	
	if any(result):
		click.echo()
		for res in reversed(result):
			nom,adresse,nums = res
			click.secho(nom, fg='cyan',bold=True)
			click.echo(adresse.strip())

			for n in nums:
				typ, num = n
				sep = ' :' if typ!='' else ''
				click.echo("    "+typ+sep+' ', nl=False)
				click.secho(num,fg='red', bold=True)
			click.echo()

	else:
		click.echo("Aucun résultat")

if __name__== '__main__':
	main()
