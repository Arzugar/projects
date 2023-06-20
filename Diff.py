#!/usr/bin/python3

import click


@click.command()
@click.option('-q', '--quick', is_flag=True, help="[Flag] indique uniquement si les 2 fichiers sont identiques.")
@click.option('-c', '--context', help="Affiche N lignes de contexte au dessus et en dessous.", type=int)
# @click.option('-w', '--large', is_flag=True, help="[Flag] active la mise en paragraphe")
@click.option('--old', is_flag=True, help="Désactive la mise en paragraphe et utilise l'ancienne version d'affichage")
@click.option('-f', '--force', is_flag=True, help="Force l'affichage des fichiers même s'ils sont identiques")
@click.argument('file_1', type=str)
@click.argument('file_2', type=str)
def difference(file_1, file_2, context, quick, force, old):
    """Outil pour repérer les différences entre 2 fichiers texte. V2"""

    if quick and force:
        click.echo("Les options --quick et --force sont incompatibles", err=True)
        return
    with open(file_1, 'r') as f1, open(file_2, 'r') as f2:  # ouvre les 2 fichiers sélectionnés

        text1, text2 = f1.readlines(), f2.readlines()  # lis le contenu des fichiers

        if (quick or text1 == text2) and not force:
            # Si les 2 fichiers sont identiques ou que l'option `quick` est activée, affiche fichier 1 == fichier  2
            click.echo(click.style('Les fichiers sont ' + ('identiques' if text1 == text2 else 'différents'),
                                   fg=('green' if text1 == text2 else 'red'), bold=True))

        else:  # cas global d'affichage cote à cote en comparaison ligne par ligne

            shell_size = click.termui.get_terminal_size()  # enregistre la taille du shell avant de la modifier

            # Affiche le texte généré par genere_text
            click.echo_via_pager(genere_text(text1, text2, context, old))

            # Remet le shell à sa taille normale
            click.echo(f'\033[8;{shell_size[1]};{shell_size[0]}t')
            # Nettoie le shell
            click.clear()


def genere_text(text1, text2, context, old):
    index_max = max(len(text1), len(text2))  # calcul de l'index de ligne maximum
    if context:  # trouve la première différence si demandé par l'argument context
        for i in range(index_max):
            try:
                if text1[i] != text2[i]:
                    break
            except IndexError:
                break
        else:
            i = index_max
        # Définit les indexes des lignes à afficher en fonction de la ligne à laquelle apparaît la première différence

        st = i - context if i - context >= 0 else 0  # dé
        index_max = i + context + 1 if i + context + 1 <= index_max + 1 else index_max + 1
    else:
        st = 0  # indexe de départ par défaut (affiche tout le document)

    rien = '[NOTHING HERE]'  # Texte correspondant à une absence de données (pour les fichiers de taille différente)

    # mesure les largeurs maximales de lignes de chaque fichier dans la zone étudiée

    long_max_1 = max(list(map(len, list(map(repr, text1[st:index_max])))))
    long_max_2 = max(list(map(len, list(map(repr, text2[st:index_max])))))

    # modifie la taille du shell en conséquence afin de n'afficher que le nécessaire

    click.echo(
        # f'\033[8;{(index_max - st + 1) if (index_max - st + 1) < 30 else 30};{(long_max_1 + long_max_2 + 5 + len(str(index_max))) if (long_max_1 + long_max_2 + 5 + len(str(index_max))) < 125 else 125}t'
    	f'\033[8;{(index_max - st + 1) if (index_max - st + 1) < 30 else 30};{125}t'

    )

    text_final = []

    # Bouche qui itère à traver les lignes à afficher et en génère un représentation
    for i in range(st, index_max):

        # Définit la représentation de la ligne du premier ficher : soit repr(ligne) pour avoir les '\n' explicites
        # soit le rien définit plus haut si arrivé au bout du fichier
        try:
            colonne_1 = repr(text1[i])[1:-1]
        except IndexError:
            colonne_1 = rien

        # Même chose pour le 2e fichier
        try:
            colonne_2 = repr(text2[i])[1:-1]
        except IndexError:
            colonne_2 = rien

        # remplace les tabulations par des espaces
        colonne_1 = colonne_1.replace(chr(9), '    ')
        colonne_2 = colonne_2.replace(chr(9), '    ')

        # Définit la couleur de la ligne pour marquer ou non une différence
        if colonne_1 != colonne_2:
            couleur_ligne = 'red'
        else:
            couleur_ligne = 'green'

        # Choisit l'activation des paragraphes en fonction de `old`
        if old:  # Cas execptionnel je le laisse au cas où mais normalement jamais besoin
            line_number_render = click.style(("{index: <" + str(len(str(index_max))) + "d}| ").format(index=i + 1),
                                             fg='cyan', bold=True)
            separateur_render = click.style("|", fg='cyan', bold=True)

            colone_1_render = click.style(("{l1: <" + str(long_max_1) + "s} ").format(l1=colonne_1),
                                          fg=(couleur_ligne if colonne_1 != rien else 'blue'),
                                          bold=colonne_1 != colonne_2 and colonne_1 != rien)

            colone_2_render = click.style((" {l2: <" + str(long_max_2) + "s}").format(l2=colonne_2),
                                          fg=(couleur_ligne if colonne_2 != rien else 'blue'),
                                          bold=colonne_1 != colonne_2 and colonne_2 != rien)

            text_final.append(line_number_render + colone_1_render + separateur_render + colone_2_render)

        else:  # Cas normal
            # appelle la fonction splitter qui découpe les lignes et les assemble pour tenir dans le cadre
            double_colonnes_render = spliter(colonne_1, colonne_2, ((125 - len(str(index_max)) - 3) // 2 - 1),
                                             index_max, i, colonne_1 != colonne_2, rien)
            text_final.append(double_colonnes_render)
    # text_final et celui qui va être afficher pas less
    return '\n'.join(text_final)


# Fonction de découpe et d'assemblage des lignes
def spliter(colonne_1, colonne_2, taille, index_max, line_index, differentes, rien):
    # Découpe les lignes en morceaux qui rentre dans une colonne
    colonne_1_split = []
    colonne_2_split = []
    for j in range(len(colonne_1) // taille + (1 if len(colonne_1) % taille != 0 else 0)):
        colonne_1_split.append(colonne_1[(j * taille):((j + 1) * taille)])

    for j in range(len(colonne_2) // taille + (1 if len(colonne_2) % taille != 0 else 0)):
        colonne_2_split.append(colonne_2[(j * taille):((j + 1) * taille)])

    split_index_max = max(len(colonne_1_split), len(colonne_2_split))

    # assemble les morceaux des 2 colonnes

    assemblage = []
    for k in range(split_index_max):
        # Définit les 2 morceaux à assembler
        try:
            col_1 = colonne_1_split[k]
        except IndexError:
            col_1 = ''
        try:
            col_2 = colonne_2_split[k]
        except IndexError:
            col_2 = ''

        # Définit le formatage du numérotage des ligne selon si la ligne de texte prend plusieurs lignes
        # d'affichage

        if split_index_max == 1:  # Case sans multilignes
            numerotation = click.style(("{index: <" + str(len(str(index_max))) + "d}| ").format(index=line_index + 1),
                                       fg='cyan', bold=False)

        else:
            if k == 0:  # Première ligne d'un block multiligne : met le numéro de ligne
                numerotation = click.style(
                    ("{index: <" + str(len(str(index_max))) + "d}| ").format(index=line_index + 1), fg='cyan',
                    bold=True)

            else:  # Block multiligne, ne répète pas le numéro
                numerotation = (len(str(index_max))) * ' ' + click.style("| ", fg='cyan', bold=True)

        premiere_colonne = click.style(("{l1: <" + str(taille) + "s} ").format(l1=col_1),
                                       fg=(('red' if differentes else 'green') if colonne_1 != rien else 'blue'),
                                       bold=differentes and colonne_1 != rien)
        separateur_milieu = click.style("|", fg='cyan', bold=split_index_max != 1)

        seconde_colonne = click.style((" {l2: <" + str(taille) + "s}").format(l2=col_2),
                                      fg=(('red' if differentes else 'green') if colonne_2 != rien else 'blue'),
                                      bold=differentes and colonne_2 != rien)

        assemblage.append(numerotation + premiere_colonne + separateur_milieu + seconde_colonne)
    click.echo(assemblage)
    return '\n'.join(assemblage)


if __name__ == '__main__':
    difference()
