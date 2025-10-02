import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib import patches

# Configuração da página
st.set_page_config(
    page_title="70 Anos de Evolução Musical",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar e preparar dados
@st.cache_data
def load_data():
    # Carregar dados
    df = pd.read_csv('music.csv')

    
    
    # Verificar se já tem decade
    if 'decade' not in df.columns:
        if 'release_date' in df.columns:
            df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
            df['decade'] = (df['release_date'].dt.year // 10) * 10
        elif 'year' in df.columns:
            df['decade'] = (df['year'] // 10) * 10
        else:
            st.error("❌ Dataset não tem coluna de data/ano!")
            st.stop()
    
    # Criar mood_category se não existir
    if 'mood_category' not in df.columns:
        valence_median = df['valence'].median()
        energy_median = df['energy'].median()
        
        conditions = [
            (df['valence'] >= valence_median) & (df['energy'] >= energy_median),
            (df['valence'] < valence_median) & (df['energy'] >= energy_median),
            (df['valence'] < valence_median) & (df['energy'] < energy_median),
            (df['valence'] >= valence_median) & (df['energy'] < energy_median)
        ]
        categories = ['Happy/Energetic', 'Angry/Tense', 'Sad/Calm', 'Peaceful/Content']
        
        # CORREÇÃO DO ERRO: Especificar default como string
        df['mood_category'] = np.select(conditions, categories, default='Unknown')
    
    return df

# Carregar dados
df = load_data()
st.sidebar.write("DEBUG - Décadas únicas no dataset:")
st.sidebar.write(sorted(df['decade'].unique()))
st.sidebar.write(f"Tipo da coluna decade: {df['decade'].dtype}")

# HEADER
st.markdown('<div class="main-header">🎵 70 Anos de Evolução Musical (1950-2019)</div>', unsafe_allow_html=True)

# SIDEBAR - Filtros
st.sidebar.header("🎛️ Filtros")
st.sidebar.markdown("---")

# Filtro de década
decades_options = sorted(df['decade'].unique())
selected_decades = st.sidebar.multiselect(
    "📅 Selecione as Décadas",
    options=decades_options,
    default=decades_options
)

# Filtro de gênero
genres = sorted(df['genre'].unique())
selected_genres = st.sidebar.multiselect(
    "🎸 Selecione os Gêneros",
    options=genres,
    default=genres
)

# Filtro de mood
moods = sorted(df['mood_category'].unique())
selected_moods = st.sidebar.multiselect(
    "🎭 Selecione os Humores",
    options=moods,
    default=moods
)

# Aplicar filtros
df_filtered = df[
    (df['decade'].isin(selected_decades)) &
    (df['genre'].isin(selected_genres)) &
    (df['mood_category'].isin(selected_moods))
]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 **{len(df_filtered):,}** músicas selecionadas de **{len(df):,}** totais")

# TABS PRINCIPAIS
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🎭 Análise de Humor", "📈 Evolução Temática", "🔍 Insights Principais"])

# =============================================
# TAB 1: VISÃO GERAL
# =============================================
with tab1:
    # KPIs no topo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎵 Total de Músicas",
            value=f"{len(df_filtered):,}",
            delta=f"{len(df_filtered)/len(df)*100:.1f}% do total"
        )
    
    with col2:
        n_artists = df_filtered['artist_name'].nunique()
        st.metric(
            label="👨‍🎤 Artistas Únicos",
            value=f"{n_artists:,}"
        )
    
    with col3:
        n_genres = df_filtered['genre'].nunique()
        st.metric(
            label="🎸 Gêneros",
            value=f"{n_genres}"
        )
    
    with col4:
        period = f"{int(df_filtered['decade'].min())}s-{int(df_filtered['decade'].max())}s"
        st.metric(
            label="📅 Período",
            value=period
        )
    
    st.markdown("---")
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por Década")
        
        decade_counts = df_filtered['decade'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(decade_counts.index, decade_counts.values, 
                      color='#667eea', edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Adicionar valores nas barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax.set_xlabel('Década', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Músicas', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.subheader("🎸 Top 10 Gêneros")
        
        top_genres = df_filtered['genre'].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Spectral(np.linspace(0, 1, len(top_genres)))
        bars = ax.barh(range(len(top_genres)), top_genres.values, color=colors, 
                       edgecolor='black', linewidth=1.5)
        
        ax.set_yticks(range(len(top_genres)))
        ax.set_yticklabels(top_genres.index, fontsize=11)
        ax.set_xlabel('Número de Músicas', fontsize=12, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Adicionar valores
        for i, (bar, val) in enumerate(zip(bars, top_genres.values)):
            ax.text(val + 5, i, f'{val}', va='center', fontweight='bold', fontsize=10)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Audio Features Evolution
    st.subheader("🎼 Evolução das Características Musicais")
    
    audio_features = ['danceability', 'energy', 'valence', 'acousticness']
    features_by_decade = df_filtered.groupby('decade')[audio_features].mean()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    colors_features = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
    markers = ['o', 's', '^', 'D']
    
    for feature, color, marker in zip(audio_features, colors_features, markers):
        ax.plot(features_by_decade.index, features_by_decade[feature],
               marker=marker, linewidth=3, markersize=10, label=feature.capitalize(),
               color=color, alpha=0.8)
    
    ax.set_xlabel('Década', fontsize=13, fontweight='bold')
    ax.set_ylabel('Valor Médio (0-1)', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=12, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    st.pyplot(fig)

# =============================================
# TAB 2: ANÁLISE DE HUMOR
# =============================================
with tab2:
    st.header("🎭 Mapa de Humor Musical")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Valence × Energy: Quadrantes Emocionais")
        
        # Scatter plot dos moods
        fig, ax = plt.subplots(figsize=(12, 10))
        
        colors_mood = {
            'Happy/Energetic': '#FFD700',
            'Angry/Tense': '#FF4444',
            'Sad/Calm': '#4169E1',
            'Peaceful/Content': '#90EE90'
        }
        
        for mood, color in colors_mood.items():
            mask = df_filtered['mood_category'] == mood
            ax.scatter(df_filtered[mask]['valence'], 
                      df_filtered[mask]['energy'],
                      c=color, label=mood, alpha=0.6, s=30,
                      edgecolors='black', linewidth=0.5)
        
        # Linhas de divisão
        valence_median = df_filtered['valence'].median()
        energy_median = df_filtered['energy'].median()
        
        ax.axhline(y=energy_median, color='black', linestyle='--', linewidth=2, alpha=0.5)
        ax.axvline(x=valence_median, color='black', linestyle='--', linewidth=2, alpha=0.5)
        
        # Labels dos quadrantes
        ax.text(0.75, 0.75, 'Happy/Energetic', fontsize=12, fontweight='bold',
               ha='center', bbox=dict(boxstyle='round', facecolor='#FFD700', alpha=0.7))
        ax.text(0.25, 0.75, 'Angry/Tense', fontsize=12, fontweight='bold',
               ha='center', bbox=dict(boxstyle='round', facecolor='#FF4444', alpha=0.7))
        ax.text(0.25, 0.25, 'Sad/Calm', fontsize=12, fontweight='bold',
               ha='center', bbox=dict(boxstyle='round', facecolor='#4169E1', alpha=0.7))
        ax.text(0.75, 0.25, 'Peaceful/Content', fontsize=12, fontweight='bold',
               ha='center', bbox=dict(boxstyle='round', facecolor='#90EE90', alpha=0.7))
        
        ax.set_xlabel('Valence (Triste ← → Feliz)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Energy (Calmo ← → Energético)', fontsize=13, fontweight='bold')
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.subheader("📊 Distribuição de Humores")
        
        mood_dist = df_filtered['mood_category'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors_pie = [colors_mood[mood] for mood in mood_dist.index]
        explode = [0.05] * len(mood_dist)
        
        wedges, texts, autotexts = ax.pie(
            mood_dist,
            labels=[f"{mood}\n({count:,})" for mood, count in mood_dist.items()],
            autopct='%1.1f%%',
            colors=colors_pie,
            startangle=90,
            explode=explode,
            shadow=True,
            textprops={'fontsize': 10, 'fontweight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Insight box
        st.markdown("""
        <div class="insight-box">
        <strong>💡 Insight:</strong><br>
        Bimodalidade emocional! ~60% das músicas estão nos extremos 
        (muito felizes ou muito tristes), enquanto apenas ~40% têm 
        emoções "mistas" (peaceful/angry).
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Evolução dos moods por década
    st.subheader("📈 Evolução dos Humores ao Longo das Décadas")
    
    mood_by_decade = pd.crosstab(df_filtered['decade'], 
                                  df_filtered['mood_category'], 
                                  normalize='index') * 100
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    mood_by_decade.plot(kind='bar', stacked=True, ax=ax,
                       color=[colors_mood[m] for m in mood_by_decade.columns],
                       edgecolor='black', linewidth=1.5, width=0.7)
    
    ax.set_xlabel('Década', fontsize=13, fontweight='bold')
    ax.set_ylabel('Percentual (%)', fontsize=13, fontweight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(title='Mood Category', fontsize=11, title_fontsize=12)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig)

# =============================================
# TAB 3: EVOLUÇÃO TEMÁTICA
# =============================================
with tab3:
    st.header("📈 Evolução dos Temas Musicais")
    
    temas = ['romantic', 'obscene', 'violence', 'sadness', 'family/spiritual']
    temas_por_decada = df_filtered.groupby('decade')[temas].mean()
    
    # Calcular variações
    primeira_decada = temas_por_decada.iloc[0]
    ultima_decada = temas_por_decada.iloc[-1]
    variacao = ((ultima_decada - primeira_decada) / primeira_decada * 100).sort_values(ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Linha do Tempo dos Principais Temas")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        cores_temas = {
            'romantic': '#FF69B4',
            'obscene': '#DC143C',
            'violence': '#8B0000',
            'sadness': '#4169E1',
            'family/spiritual': '#9370DB'
        }
        
        for tema in temas:
            ax.plot(temas_por_decada.index, temas_por_decada[tema],
                   marker='o', linewidth=3, markersize=9,
                   label=tema.upper(), color=cores_temas[tema], alpha=0.8)
            
            # Anotação no último ponto
            ultimo_valor = temas_por_decada[tema].iloc[-1]
            var_pct = variacao[tema]
            ax.annotate(f'{var_pct:+.0f}%',
                       xy=(temas_por_decada.index[-1], ultimo_valor),
                       xytext=(10, 0), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       color=cores_temas[tema],
                       bbox=dict(boxstyle='round', facecolor='white',
                                edgecolor=cores_temas[tema], linewidth=2))
        
        ax.set_xlabel('Década', fontsize=13, fontweight='bold')
        ax.set_ylabel('Intensidade Média', fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=11, frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.subheader("🔺🔻 Variação Total")
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        cores_var = ['green' if x > 0 else 'red' for x in variacao]
        bars = ax.barh(range(len(variacao)), variacao.values,
                      color=cores_var, alpha=0.7,
                      edgecolor='black', linewidth=2)
        
        ax.set_yticks(range(len(variacao)))
        ax.set_yticklabels(variacao.index, fontsize=11, fontweight='bold')
        ax.set_xlabel('Variação (%)', fontsize=12, fontweight='bold')
        ax.axvline(x=0, color='black', linewidth=2)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Adicionar valores
        for i, (val, bar) in enumerate(zip(variacao.values, bars)):
            ax.text(val + (5 if val > 0 else -5), i, f'{val:+.0f}%',
                   va='center', ha='left' if val > 0 else 'right',
                   fontweight='bold', fontsize=10)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Heatmap
    st.subheader("🌡️ Heatmap: Intensidade dos Temas por Década")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(temas_por_decada.T, annot=True, fmt='.3f',
               cmap='YlOrRd', linewidths=2, linecolor='white',
               cbar_kws={'label': 'Intensidade Média'}, ax=ax)
    
    ax.set_xlabel('Década', fontsize=13, fontweight='bold')
    ax.set_ylabel('Tema', fontsize=13, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)

# =============================================
# TAB 4: INSIGHTS PRINCIPAIS
# =============================================
with tab4:
    st.header("💡 Principais Descobertas")
    
    # Insight 1
    st.markdown("""
    ### 1. 💔 A Morte do Romance Clássico
    
    <div class="insight-box">
    O tema <strong>romântico</strong> despencou <strong>77%</strong> em 70 anos, saindo de 12.1% 
    das músicas nos anos 50 para apenas 2.8% nos anos 2010. 
    <br><br>
    <strong>Interpretação:</strong> Passamos de baladas idealizadas sobre amor eterno 
    para abordagens mais realistas, cínicas ou sexualizadas. O amor mudou - e a música reflete isso.
    </div>
    """, unsafe_allow_html=True)
    
    # Insight 2
    st.markdown("""
    ### 2. 🔞 A Ascensão do Explícito
    
    <div class="insight-box">
    Conteúdo <strong>obsceno</strong> aumentou <strong>+178%</strong> e <strong>violência</strong> 
    cresceu <strong>+144%</strong>.
    <br><br>
    <strong>Interpretação:</strong> A música reflete uma sociedade menos reprimida, 
    mas também mais confrontativa. Hip-Hop/Rap trouxe linguagem mais direta e 
    sem filtros para o mainstream.
    </div>
    """, unsafe_allow_html=True)
    
    # Insight 3
    st.markdown("""
    ### 3. 🎭 Bimodalidade Emocional
    
    <div class="insight-box">
    Cerca de <strong>60%</strong> das músicas estão nos extremos emocionais: 
    ou muito felizes/energéticas (30%) ou muito tristes/calmas (30%).
    <br><br>
    <strong>Interpretação:</strong> As pessoas buscam música principalmente para 
    <strong>celebrar momentos alegres</strong> ou <strong>processar emoções difíceis</strong>. 
    Estados emocionais "neutros" são menos procurados.
    </div>
    """, unsafe_allow_html=True)
    
    # Insight 4
    st.markdown("""
    ### 4. 📉 Do Sentimentalismo ao Cinismo
    
    <div class="insight-box">
    Saímos de uma era sentimental (romance 12%, tristeza 14%) para uma era mais 
    crua (obscenidade 16%, violência 14%).
    <br><br>
    <strong>Interpretação:</strong> A música deixou de ser "escape da realidade" 
    para ser "espelho da realidade". Menos idealização, mais autenticidade (ou cinismo).
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Resumo em números
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
        <h3 style="color: #FF6B6B;">🔺 Maior Crescimento</h3>
        <h2>Obscene</h2>
        <p style="font-size: 1.5rem; font-weight: bold; color: green;">+178%</p>
        <p>De 5.7% → 16% das músicas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
        <h3 style="color: #4169E1;">🔻 Maior Declínio</h3>
        <h2>Romantic</h2>
        <p style="font-size: 1.5rem; font-weight: bold; color: red;">-77%</p>
        <p>De 12.1% → 2.8% das músicas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
        <h3 style="color: #FFD700;">🎭 Mood Dominante</h3>
        <h2>Happy/Energetic</h2>
        <p style="font-size: 1.5rem; font-weight: bold;">~30%</p>
        <p>Empatado com Sad/Calm</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Conclusão
    st.markdown("""
    ### 🎯 Conclusão
    
    A análise de 70 anos de música popular revela uma **transformação cultural profunda**:
    
    - 🎵 **Menos idealização, mais realidade**: Romance e poesia declinaram
    - 🔓 **Liberalização cultural**: Conteúdo explícito triplicou
    - ⚡ **Música mais crua**: Violência e confronto aumentaram
    - 🎭 **Extremos emocionais**: Público busca catarse (felicidade ou tristeza intensa)
    
    A música não apenas entretém - ela **espelha e documenta** as mudanças na sociedade.
    """)

# FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>🎵 Dashboard de Análise Musical</strong></p>
    <p>Dados: Kaggle Music Dataset (1950-2019) | Desenvolvido com Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)