from langchain.prompts import PromptTemplate


code_explaination_prompt = """

Human: Here is some java code:

<context>
{context}
</context>

Understand the provided code carefully and answer according to the following instructions:

1. Name: Give the name of the file/code class
2. Purpose: Explain what the code does in one sentence
3. Functionalities: Give a few bullet points describing the functionalities of the code 

answer without using too much space. Don't add space between each bullet points line.

Assistant:"""


CODE_EXPLANATION = PromptTemplate(
    template=code_explaination_prompt, input_variables=["context"]
)

code_comparaison_prompt = """

Human: Here are 2 pieces of java code from 2 application BILLI and FAM:

This is BILLI's code:
<code1>
{billi_code}
</code1>

This is FAM's code:
<code2>
{fam_code}
</code2>

Understand the provided code carefully, answer according to the following instructions and explain in detail your answers:

1. What are the functional differences between BILLI's and FAM's code?
2. What are the functional similarities between BILLI's and FAM's code?
3. Say how similar are the codes using a scale from 0 to 10 
    (0 if they are not doing the same thing, 10 if they are doing exactly the same thing)

aswer whithout using too much space. Don't add space between each bullet points line.

Assistant:"""


CODE_COMPARAISON = PromptTemplate(
    template=code_comparaison_prompt, input_variables=["billi_code", "fam_code"]
)

# code_comparaison_prompt_FR = """

# Human: Voici deux codes Java des applications BILLI et FAM:

# This is BILLI's code:
# <code1>
# {billi_code}
# </code1>

# This is FAM's code:
# <code2>
# {fam_code}
# </code2>

# répond selon les instructions suivantes en respectant la structure:

# **FAM**: ce que fait ce code en une phrase
# **BILLI** ce que fait ce code en une phrase
# **Difference** : Quelles sont les différences fonctionnelles entre ces codes? repondre en quelques bullet point
# **Similitude** : Quelles sont les similitudes fonctionnelles entre ces codes?  repondre en quelques bullet point
# **Score** : .../10 (note à quel point les codes sont similaires en utilisant une échelle de 0 à 10
#                 0 s'ils ne font pas la même chose, 10 s'ils font exactement la même chose

# Répondre en français sans utiliser trop d'espace. Ne dit pas "il est difficile de déterminer les similitudes" ou "il est difficile de déterminer les différences"

# Assistant:"""


code_comparaison_prompt_FR = """

Human: Voici deux codes:

Voici le premier code:
<code1>
{billi_code}
</code1>

Voici le deuxieme code:
<code2>
{fam_code}
</code2>

répond selon les instructions suivantes en respectant la structure:

**Difference** : Quelles sont les différences fonctionnelles entre ces codes? repondre en quelques bullet point
**Similitude** : Quelles sont les similitudes fonctionnelles entre ces codes?  repondre en quelques bullet point
**Score** : .../10 (note à quel point les codes sont similaires en utilisant une échelle de 0 à 10
                0 s'ils ne font pas la même chose, 10 s'ils font exactement la même chose

Répondre en français sans utiliser trop d'espace. Ne dit pas "il est difficile de déterminer les similitudes" ou "il est difficile de déterminer les différences"

Assistant:"""


# **Remarque** : Une remarque pour aider a la decision pour integrer ce que fait ce bout de code FAM en plus dans le code de BILLI


CODE_COMPARAISON_FR = PromptTemplate(
    template=code_comparaison_prompt_FR, input_variables=["billi_code", "fam_code"]
)





code_extraction_prompt = """

Human: Here is a piece of java code your goal is to extract the part of code that match the most the descripton:
<code>
{code}
</code>

<description>
{description}
</description>

Answer as follow:

Here is the piece of code that matches with the description:
<code>
Include the corresponding piece of code
</code>

Assistant:"""


CODE_EXTRACT = PromptTemplate(
    template=code_extraction_prompt, input_variables=["code", "description"]
)

codebase_description_prompt = """

Human: Here is a piece of code, your goal is to answer the question regarding the code
<code>
{code}
</code>

<Question>
{question}
</Question>

Answer as follow:
1. Answer to the question
2. Say which class is the most relevant for answering the question

Assistant:"""


CODE_BASE_DESCRIPTION = PromptTemplate(
    template=codebase_description_prompt, input_variables=["code", "question"]
)


code_documentation_prompt = """
Human: Voici un segment d'une grande base de code java, ton role est de fournir une description compréhensible par {target}.

Voici le code:
<code>
{code}
</code>

répond en donnant simplement une description la plus courte possible et en un paragraphe maximum pour explique a {target} ce que fait ce code.
Ta reponse sera en fraçais, repond en donnant uniquement cette description.
Ecirs les information sous format markdown mais tu dois essayer le plus possible de ne pas citer des noms de fonctions.
Tu n'as pas besoin de rappeler qu'il sagit d'un code Java.
Assistant:"""

CODE_DOCUMENTATION = PromptTemplate(
    template=code_documentation_prompt, input_variables=["target", "code"]
)

documentation_summary_prompt = """
Human: Voici la documentation simplifiée d'une base de code. Ton rôle est de la résumer.
<doc>
{documentation}
</doc>

répond en donnant simplement une description la plus courte possible et en un paragraphe maximum pour explique a {target} ce que fait cette base de code.
Ta reponse sera en fraçais, repond en donnant directement et uniquement le résumé.

Assistant:"""

DOCUMENTATION_SUMMARY = PromptTemplate(
    template=documentation_summary_prompt, input_variables=["target", "documentation"]
)



gap_summary_prompt = """
Human: Voici la documentation simplifiée d'une base de code. Ton rôle est de la résumer.
<doc>
{documentation}
</doc>

répond en donnant simplement un résumé des différences majeures entre BILLI et FAM.
Ta reponse sera en fraçais, repond en donnant directement et uniquement la reponse.

Assistant:"""

GAP_SUMMARY = PromptTemplate(
    template=gap_summary_prompt, input_variables=["documentation"]
)



# FAM_CODE_DEMO = """
# Human: Voici un segment d'une grande base de code java, ton role est de fournir une description compréhensible par {target}.

# Voici le code:
# <code>
# {code}
# </code>

# répond en donnant simplement une description la plus courte possible et en un paragraphe maximum pour explique a {target} ce que fait ce code.
# Ta reponse sera en fraçais, repond en donnant uniquement cette description.
# Ecirs les information sous format markdown mais tu dois essayer le plus possible de ne pas citer des noms de fonctions.
# Tu n'as pas besoin de rappeler qu'il sagit d'un code Java.
# Assistant:"""