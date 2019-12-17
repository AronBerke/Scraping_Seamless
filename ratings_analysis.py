import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
plt.style.use('ggplot')
import seaborn as sns
import re

# read in restaurant data
rest = pd.read_csv('rest_data2.csv')
rest = rest.set_index('name')

#remove restaurants with less than 30 ratings
rest = rest[rest.num_ratings>=30]

#get initial picture of resulting dataframe
print(rest.shape)
rest.describe()

#inspect ratings distribution
rest.groupby('rating')['rating'].count().plot.bar(width=1.0)
plt.ylabel('count')

#cuisine category column was stored as a string and is converted to a list below
cats = rest.category.map(lambda x: x.split())
rest['category']=cats

#define function to clean cuisine lists in the category column
def clean_cats(cat_lis):
    temp = []
    for x in cat_lis:
        try:
            cuis = re.search('[A-Z]+[a-z]*',x).group()
        except:
            cuis='blank'
        temp.append(cuis)
    return(temp)

#apply clean fucntion to the category column and reassign
final_cats = rest.category.map(lambda x: clean_cats(x))
rest['category']=final_cats

#find the restaurants with category values not matching the regex patter in clean_cats function and manually replace
rest.loc[rest.category.map(lambda x: 'blank' in x)]
rest.category['Creamline Burgers and Shakes']=['Hamburgers']

#create long form data frame with category stacked
exploded = rest.category.apply(pd.Series).stack().reset_index(level=0).rename(columns={0:'category'})
exploded.set_index('name', inplace=True)

#create new df with category dropped to merge with long form dataframe containing stacked categories and merge
rest_lform = rest.drop('category',1)
rest_lform = pd.merge(rest_lform, exploded, on='name')

#view counts for each food type and manually extract cuisine ethnicities with freq >30
#American, Japanese, Italian, Chinese, Mexican, Indian, Thai, Middle Easter
rest_lform.groupby('category')['rating'].agg(['mean','count'])\
      .sort_values('count', ascending = False)

#create list of cuisines of interest and prune long form dataset to focus on them
cuisines = ['American', 'Japanese', 'Italian', 'Chinese', 'Mexican', 'Indian', 'Thai', 'Middle']
lform_cuisines = rest_lform[rest_lform.category.isin(cuisines)]
lform_cuisines.groupby('category')['rating'].agg(['mean', 'std', 'count','median'])

#import stats model and define arrays for each cuisine type
from scipy import stats

American = np.array(lform_cuisines[lform_cuisines.category=='American']['rating'])
Japanese = np.array(lform_cuisines[lform_cuisines.category=='Japanese']['rating'])
Italian = np.array(lform_cuisines[lform_cuisines.category=='Italian']['rating'])
Chinese = np.array(lform_cuisines[lform_cuisines.category=='Chinese']['rating'])
Mexican = np.array(lform_cuisines[lform_cuisines.category=='Mexican']['rating'])
Indian = np.array(lform_cuisines[lform_cuisines.category=='Indian']['rating'])
Thai = np.array(lform_cuisines[lform_cuisines.category=='Thai']['rating'])
Middle_Eastern = Indian = np.array(lform_cuisines[lform_cuisines.category=='Middle']['rating'])

#check that equality of variances condition holds, then perform one-way anova and kruskal-wallis
#ANOVA is likely better due to pseudo-interval/ordinal data type
#perform pairwise tests for Japanese and Italian against all others
print(stats.bartlett(American, Japanese, Italian, Chinese, Mexican, Indian, Thai, Middle_Eastern))
print(stats.f_oneway(American, Japanese, Italian, Chinese, Mexican, Indian, Thai, Middle_Eastern))
print(stats.kruskal(American, Japanese, Italian, Chinese, Mexican, Indian, Thai, Middle_Eastern))
cuisines = [Japanese, American, Italian, Chinese, Mexican, Indian, Thai, Middle_Eastern]
for cuisine in cuisines:
    print(stats.ttest_ind(Japanese, cuisine))
for cuisine in cuisines:
    print(stats.ttest_ind(Italian, cuisine))

#potential highly stylized visualization of distributions by cuisine category
lform_cuisines[lform_cuisines.category=='American']['rating'].plot(kind='density',color = "#9a9c9a")
lform_cuisines[lform_cuisines.category=='Mexican']['rating'].plot(kind='density', color ="#9a9c9a")
lform_cuisines[lform_cuisines.category=='Indian']['rating'].plot(kind='density', color = "#9a9c9a")
lform_cuisines[lform_cuisines.category=='Middle']['rating'].plot(kind='density', color = "#9a9c9a")
lform_cuisines[lform_cuisines.category=='Thai']['rating'].plot(kind='density', linewidth=3)
lform_cuisines[lform_cuisines.category=='Chinese']['rating'].plot(kind='density', linewidth=3)
lform_cuisines[lform_cuisines.category=='Japanese']['rating'].plot(kind='density',linewidth=3)
lform_cuisines[lform_cuisines.category=='Italian']['rating'].plot(kind='density', linewidth=3)

#generate plot showing mean rating by cuisine type
data = pd.DataFrame(lform_cuisines.groupby('category')['rating'].mean().sort_values(ascending=False))
data = data.reset_index(level=0)
plot = sns.barplot(x=data.category, y=data.rating)
for p in plot.patches:
    height = p.get_height()
    plot.text(p.get_x()+p.get_width()/2.,
            height+.1,
            '{:1.2f}'.format(height),
            ha="center") 
plot.set_xlabel("Category",fontsize=12)
plot.set_ylabel("Rating (mean)", fontsize=12)
sns.set_style({'text.color':'#000000'})
plt.show()

#generate plot showing correlation of quality and rating
sns.lmplot('quality_perc', 'rating', data=rest, y_jitter=0.25, line_kws={'color':'#34A5DA'}, scatter_kws={'color':'#34A5DA'})
plt.xlabel('Quality Percentage', fontsize=12)
plt.ylabel('Rating', fontsize=12)
print(stats.pearsonr(rest.quality_perc, rest.rating))

#generate plot showing correlation of order timeliness and rating
sns.lmplot('ontime_perc', 'rating', data=rest, y_jitter=0.25, line_kws={'color':'#C52060'}, scatter_kws={'color':'#C52060'})
plt.xlabel('On-Time Percentage', fontsize=12)
plt.ylabel('Rating', fontsize=12)
print(stats.pearsonr(rest.ontime_perc, rest.rating))

#generate plot showing correlation of order accuracy and rating
sns.lmplot('accuracy_perc', 'rating', data=rest, y_jitter=0.25, line_kws={'color':'#3F969A'}, scatter_kws={'color':'#3F969A'})
plt.xlabel('Accuracy Percentage', fontsize=12)
plt.ylabel('Rating', fontsize=12)
print(stats.pearsonr(rest.accuracy_perc, rest.rating))

#view correlation matrix/collinearity
corrdf = rest[['ontime_perc', 'accuracy_perc', 'quality_perc']]
corrdf.corr()

#create grouped data set to show distribution of ratings across food categories and visualize
grouped = pd.DataFrame(lform_cuisines.groupby(['category','rating'])['rating'].count())
grouped = grouped.rename(columns={'rating':'count'})
grouped = grouped.reset_index(level=0)
grouped = grouped.reset_index(level=0)
df = pd.DataFrame({'rating':[2.0,2.5,2.0,2.0,2.5,2.0,2.0,2.0,2.5,5], 'category':['Chinese','Chinese','Italian','Japanese','Japanese', 'Mexican','Middle', 'Thai','Thai','Indian'],'count':[0,0,0,0,0,0,0,0,0,0]})
grouped_all = pd.concat([df, grouped])
CatGrid = sns.FacetGrid(grouped_all, col='category', hue='category')
CatGrid.map(sns.barplot, 'rating', 'count')

#generate plot showing correlation of timeliness and rating for two different cuisine types (Chinese vs. American)
sns.lmplot("ontime_perc", "rating", 
           lform_cuisines[lform_cuisines.category.isin(['Chinese','American'])], 
           hue="category", y_jitter=0.25)
plt.xlabel('On-Time Percentage', fontsize=12)
plt.ylabel('Rating', fontsize=12)
print(stats.pearsonr(lform_cuisines[lform_cuisines.category=='American']['ontime_perc'],
                        lform_cuisines[lform_cuisines.category=='American']['rating'] ))
print(stats.pearsonr(lform_cuisines[lform_cuisines.category=='Chinese']['ontime_perc'],
                        lform_cuisines[lform_cuisines.category=='Chinese']['rating'] ))

#generate plot showing correlation of quality and rating for two different cuisine types (Chinese vs. American)
sns.lmplot("quality_perc", "rating", 
           lform_cuisines[lform_cuisines.category.isin(['Chinese','American'])], 
           hue="category", y_jitter=0.25)
plt.xlabel('Quality Percentage', fontsize=12)
plt.ylabel('Rating', fontsize=12)
print(stats.pearsonr(lform_cuisines[lform_cuisines.category=='American']['quality_perc'],
                        lform_cuisines[lform_cuisines.category=='American']['rating'] ))
print(stats.pearsonr(lform_cuisines[lform_cuisines.category=='Chinese']['quality_perc'],
                        lform_cuisines[lform_cuisines.category=='Chinese']['rating'] ))

#generate plot showing correlation of accuracy and rating for two different cuisine types (Chinese vs. American)
sns.lmplot("accuracy_perc", "rating", 
           lform_cuisines[lform_cuisines.category.isin(['Chinese','American'])], 
           hue="category", y_jitter=0.25)
plt.xlabel('Accuracy Percentage', fontsize=12)
plt.ylabel('Rating', fontsize=12)
print(stats.pearsonr(lform_cuisines[lform_cuisines.category=='American']['accuracy_perc'],
                        lform_cuisines[lform_cuisines.category=='American']['rating'] ))
print(stats.pearsonr(lform_cuisines[lform_cuisines.category=='Chinese']['accuracy_perc'],
                        lform_cuisines[lform_cuisines.category=='Chinese']['rating'] ))
