import requests
import mwparserfromhell
import wikipedia
import numpy as np

def get_wikidata_from_title(title: str,): 
    try:    
        content = wikipedia.page(title)
        parsed_wikidata = {
            "title": content.title,
            "content": content.content,
            "images": content.images,
            "links": content.links
        }
        return True, parsed_wikidata
    except:
        return False, {'error': f"Error: not a valid Wikipedia Page. Check the title and ensure you entered it correctly (title-{title})"}

print(get_wikidata_from_title("som random thing"))

def get_titles(search_query):
    return wikipedia.search(search_query.encode("utf-8"), results=20)

def edit_distance(s1, s2):
    n = len(s1)
    m = len(s2)
    #create matrix of zeroes of the lenghts of s1 and s2
    distance_matrix = np.zeros((n+1,m+1))
    #fill the empty string comparation with s1 and s2 so 1, 2, 3, 4... n
    for col in range(1,n+1):
        distance_matrix[col,0] = distance_matrix[col-1,0]+1
    for row in range(1, m+1):
        distance_matrix[0,row] = distance_matrix[0,row-1]+1
    #iterate ove the matrix and fill it
    for i in range(1,n+1):
        for j in range(1,m+1):
            #fill the matrix, if it is insertion or deletion add 1
            insertion = distance_matrix[i,j-1] + 1
            deletion = distance_matrix[i-1,j] + 1
            #if both characters are different that means substitution so the cost is 2
            if s1[i-1] != s2[j-1]:
                replace_same = distance_matrix[i-1,j-1] + 2 
            #if both characters are the same nothing is added since there is not cost
            else:
                replace_same = distance_matrix[i-1,j-1]
            #pick the min
            distance_matrix[i, j] = min([insertion, deletion, replace_same])
    #return the min distance
    return int(distance_matrix[n][m])

def get_wikidata_from_topic(topic,):
    titles = get_titles(topic)
    titles.sort(key=lambda x: edit_distance(x, topic))
    return get_wikidata_from_title(titles[0])