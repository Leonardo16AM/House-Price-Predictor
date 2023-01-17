import re

def distance(a,b):
    dp = [[0 for x in range(len(b)+1)] for y in range(len(a)+1)] 
    for i in range(len(a)+1):
        for j in range(len(b)+1):
            if i==0:dp[i][j]=j
            if j==0:dp[i][j]=i
            if i!=0 and j!=0 :
                if a[i-1]==b[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min( dp[i-1][j] , min(dp[i-1][j-1],dp[i][j-1]) )
    return dp[len(a)][len(b)]


def del_tild(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("ó", "o"),
        ("í", "i"),
        ("ú", "u"),
        ("ñ", "n"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def normalize(words):
    for i in range(len(words)):
        words[i]=words[i].lower()
        words[i]=del_tild(words[i])

    return words


def is_same_word(a,b,dif=2):
    if len(a)<=4: dif==0
    return distance(a,b)<=dif


def is_number(s):
    nums=[
        ['un','primer','1er','uno','1','primero'],
        ['dos','segundo','2do','2'],
        ['tres','tercer','3er','3'],
        ['cuatro','cuarto','4to','4'],
        ['cinco','sinco','quinto','5to','5'],
        ['seis','sexto','6to','6'],
        ['siete','septimo','7mo','7'],
        ['ocho','octavo','8vo','8'],
        ['nueve','noveno','9no','9'],
        ['diez','dies','decimo','10mo','10']
    ]
    for i in range(len(nums)):
        for n in nums[i]:
            if is_same_word(n,s,0):
                return i+1
    return -1

def negative(s):
    return s=='no'

def has_feature(feature,text):
    l1="yes"
    l2="yes"
    for fword in feature:
        for token in text:
            if type(fword)==str:
                if is_same_word(fword,token):
                    if negative(l1) or negative(l2):
                        return 0
                    else:
                        return 1
            else:
                if len(fword)==2:
                    if is_same_word(fword[0],l2) and is_same_word(fword[1],token):
                        return 1
                if len(fword)==3: 
                    if is_same_word(fword[0],l1) and is_same_word(fword[1],l2) and is_same_word(fword[2],token):
                        return 1
            l1=l2         
            l2=token
    return -1

def num_feature(feature,text):
    l1="yes"
    l2="yes"
    for fword in feature:
        for token in text:
            if type(fword)==str:
                if is_same_word(fword,token):
                    if is_number(l1)!=-1:
                        return is_number(l1)
                    if is_number(l2)!=-1:
                        return is_number(l2)
                    return 1
            l1=l2         
            l2=token
    return -1

def cuarto_as_frac(text):
    for token in text:
        if len(token)>2 and token[-1]=='4' and token[-2]=='/':
            nt=''
            for i in token:
                if i=='/':break
                nt+=i 
            return is_number(nt)
    return -1

def get_features(text):
    words=re.split('; |,|-|\.|:|!| |\*|\n',text)
    words=normalize(words)
    
    ret={}
    ynfeatures={
        'piscina':['piscina'],
        'apartamento':['apartamento'],
        'gas':['gas'],
        'amueblado':['amueblado',['todo','adentro']],
        'patio':['patio'],
        'nauta':[['nauta','hogar'],'nautahogar'],
        'cisterna':['cisterna'],
        'finca':['finca'],
        'portal':['portal'],
        'techo de placa':[['techo','de','placa']],
        'hospital':['hospitale'],
        'escuela':['escuela']
    }
    for feature in ynfeatures:
        ret[feature]=has_feature(ynfeatures[feature],words)

    numfeatures={
        'cuartos':['cuartos','habitacione'],
        'banos':['banos'],
        'salas':['sala'],
        'plantas':['plantas'],
        'cocinas':['cocina'],
        'comedores':['comedore'],
        'desahogos':['desahogo'],
        'pisos':['pisos'],
        'splits':['splits'],
        'refrigeradores':['refrigeradore'],
        'garajes':['garaje'],
        'tanques':['tanque'],
    }
    for feature in numfeatures:
        ret[feature]=num_feature(numfeatures[feature],words)
    
    if ret['cuartos']==-1:
        ret['cuartos']=cuarto_as_frac(words)   

    return ret