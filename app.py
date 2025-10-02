import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv('music.csv')
    df['release_date'] = pd.to_datetime(df['release_date'], format='%Y')
    df['genre'] = df['genre'].str.lower().str.strip()
    df['topic'] = df['topic'].str.lower().str.strip()
    df['decade'] = (df['release_date'].dt.year // 10) * 10
    return df

df = load_data()

st.set_page_config(page_title="Décadas de Som: Dashboard Musical", layout="wide", page_icon="🎵")

# Título e introdução
st.title("🎵 Décadas de Som: Dashboard Musical")
st.markdown("""
Dashboard interativo para explorar a evolução da música ao longo das décadas, com base em dados de milhares de faixas. 
Descubra tendências, mudanças culturais e perfis sonoros!
""")

# Filtros principais
col1, col2 = st.columns(2)
with col1:
    decadas = sorted(df['decade'].unique())
    decada_sel = st.multiselect("Filtrar por Década", decadas, default=decadas)
with col2:
    generos = sorted(df['genre'].unique())
    genero_sel = st.multiselect("Filtrar por Gênero", generos, default=generos[:8])

df_filt = df[df['decade'].isin(decada_sel) & df['genre'].isin(genero_sel)]

# 1. Evolução das características musicais
st.header("📈 Evolução das Características Musicais")
df_dec = df_filt.groupby('decade')[['danceability', 'energy', 'valence']].mean().reset_index()
fig1 = px.line(df_dec, x='decade', y=['danceability', 'energy', 'valence'],
               markers=True, labels={'value':'Valor Médio', 'decade':'Década', 'variable':'Característica'},
               color_discrete_map={'danceability':'#FF6B6B', 'energy':'#4ECDC4', 'valence':'#FFE66D'})
fig1.update_layout(legend_title_text='Característica', template='plotly_white')
st.plotly_chart(fig1, use_container_width=True)

# 2. Distribuição de moods
st.header("🎭 Distribuição de Moods Musicais")
valence_median = df['valence'].median()
energy_median = df['energy'].median()
def classify_mood(row):
    if row['valence'] >= valence_median and row['energy'] >= energy_median:
        return 'Happy/Energetic'
    elif row['valence'] < valence_median and row['energy'] >= energy_median:
        return 'Angry/Tense'
    elif row['valence'] < valence_median and row['energy'] < energy_median:
        return 'Sad/Calm'
    else:
        return 'Peaceful/Content'
if 'mood_category' not in df_filt.columns:
    df_filt['mood_category'] = df_filt.apply(classify_mood, axis=1)
mood_counts = df_filt['mood_category'].value_counts().reset_index()
mood_counts.columns = ['mood', 'count']
fig2 = px.pie(mood_counts, names='mood', values='count',
              color='mood', color_discrete_map={
                  'Happy/Energetic':'#FFD700', 'Sad/Calm':'#6495ED',
                  'Peaceful/Content':'#90EE90', 'Angry/Tense':'#FF6347'
              }, hole=0.4)
fig2.update_traces(textinfo='percent+label')
st.plotly_chart(fig2, use_container_width=True)

# 3. Moods por década
st.subheader("🕰️ Evolução dos Moods por Década")
mood_decade = pd.crosstab(df_filt['decade'], df_filt['mood_category'], normalize='index') * 100
fig3 = px.area(mood_decade, x=mood_decade.index, y=mood_decade.columns,
               labels={'value':'% de músicas', 'decade':'Década', 'variable':'Mood'})
fig3.update_layout(template='plotly_white')
st.plotly_chart(fig3, use_container_width=True)

# 4. Temas musicais por década
st.header("📚 Temas Musicais ao Longo das Décadas")
temas = [
    'dating', 'violence', 'world/life', 'night/time', 'shake the audience', 'family/gospel', 'romantic',
    'communication', 'obscene', 'music', 'movement/places', 'light/visual perceptions', 'family/spiritual',
    'like/girls', 'sadness', 'feelings'
]
temas_disponiveis = [t for t in temas if t in df_filt.columns]
temas_dec = df_filt.groupby('decade')[temas_disponiveis].mean().reset_index()
fig4 = px.line(temas_dec, x='decade', y=temas_disponiveis, markers=True)
fig4.update_layout(legend_title_text='Tema', template='plotly_white')
st.plotly_chart(fig4, use_container_width=True)

# 5. Destaques: temas que mais cresceram e caíram
st.subheader("🚀 Temas em Alta e em Queda (1950s vs 2010s)")
if len(temas_dec) > 1:
    primeira = temas_dec.iloc[0]
    ultima = temas_dec.iloc[-1]
    variacao = pd.DataFrame({
        'Tema': temas_disponiveis,
        'Primeira Década': primeira[temas_disponiveis].values,
        'Última Década': ultima[temas_disponiveis].values,
        'Variação (%)': ((ultima[temas_disponiveis] - primeira[temas_disponiveis]) / primeira[temas_disponiveis] * 100).values
    })
    top_cresceram = variacao.sort_values('Variação (%)', ascending=False).head(3)
    top_caíram = variacao.sort_values('Variação (%)').head(3)
    st.markdown("**Top 3 Temas que Mais Cresceram:**")
    st.dataframe(top_cresceram[['Tema', 'Variação (%)']].round(1), hide_index=True)
    st.markdown("**Top 3 Temas que Mais Diminuíram:**")
    st.dataframe(top_caíram[['Tema', 'Variação (%)']].round(1), hide_index=True)

# 6. Perfil sonoro dos moods
st.header("🔊 Perfil Sonoro de Cada Mood")
mood_profile = df_filt.groupby('mood_category')[['danceability', 'loudness', 'acousticness', 'valence', 'energy']].mean().reset_index()
fig5 = px.bar(mood_profile.melt(id_vars='mood_category'), x='variable', y='value', color='mood_category',
              barmode='group', labels={'value':'Média', 'variable':'Característica', 'mood_category':'Mood'})
fig5.update_layout(template='plotly_white')
st.plotly_chart(fig5, use_container_width=True)

# 7. Insights finais
st.header("💡 Insights Principais")
st.markdown("""
- **A música ficou mais explícita e menos romântica:** Temas como 'obscene' e 'violence' cresceram muito, enquanto 'romantic' caiu drasticamente.
- **Mudança de moods:** O equilíbrio entre músicas felizes/energéticas e tristes/calmas revela uma polarização emocional ao longo das décadas.
- **Perfil sonoro:** Músicas 'Angry/Tense' e 'Happy/Energetic' têm mais energia e loudness, enquanto 'Sad/Calm' e 'Peaceful/Content' são mais acústicas e suaves.
- **Décadas importam:** As décadas mais recentes mostram maior diversidade temática e emocional.
""")

# 8. Download dos dados filtrados
st.download_button("⬇️ Baixar dados filtrados (CSV)", df_filt.to_csv(index=False), file_name="dados_filtrados.csv")

st.caption("Dashboard desenvolvido com ❤️ para análise de tendências musicais.")