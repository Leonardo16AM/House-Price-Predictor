import re
import pandas as pd 


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



def common_sense_implications(features):
    turn_on_imps={
        'apartamento':['techo de placa'],
        'finca':['patio'] }
    turn_off_imps={
        'apartamento':['piscina','patio']
    }

    not_mentioned_imps={
        'piscina',
        'apartamento',
        'amueblado',
        'patio',
        'nauta',
        'cisterna',
        'portal',
        'techo de placa',
        'finca',
        'salas',
        'comedores',
        'desahogos',
        'pisos',
        'hospital',
        'escuela',
        'splits',
        'refrigeradores',
        'garajes'
    }
    
    for feat in not_mentioned_imps:
        if features[feat]==-1:
            features[feat]=0
    
    for imp in turn_on_imps.keys():
        for feat in turn_on_imps[imp]:
            if features[imp]!=0 and features[feat]==-1:
                features[feat]=1

    for imp in turn_off_imps.keys():
        for feat in turn_off_imps[imp]:
            if features[imp]!=0 and features[feat]==-1:
                features[feat]=0
            
    return features


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

    ret=common_sense_implications(ret)    

    return ret

def one_hot_encode(pddict, dim):
    one_hot = pd.get_dummies(pddict[dim])
    return one_hot


mfv = pd.read_csv('mean_feature_values.csv', index_col=[0])
mean_feature_values = mfv.to_dict('records')[0]

def extract_features(text, province, municipality):
    features = get_features(text)
    

    for c in mean_feature_values.keys():
        if not (c in features):
            features[c] = 0
        elif features[c] == -1:
            features[c] = mean_feature_values[c]
        if c == province or c == municipality:
            print(features[c])
            features[c] = 1
            print(features[c])
            print(c)
            

    columns = list( features.keys() )
    ret = pd.DataFrame( [list(features.values())], columns= columns )
    ret=ret.drop('price',axis=1)
    return ret
