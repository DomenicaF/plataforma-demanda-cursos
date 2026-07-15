import { useEffect, useState } from 'react'
import client from '../api/client'
import Plot, { chartLayout } from '../components/Plot.jsx'

function Kpi({ icon, bg, value, label }) {
  return (
    <div className="card">
      <div className="icon" style={{ background: bg }}>{icon}</div>
      <div>
        <div className="kpi">{value}</div>
        <div className="label">{label}</div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [demand, setDemand] = useState([])   // Google Trends (interés 0-100)
  const [supply, setSupply] = useState([])   // Udemy (nº de cursos publicados)
  const [forecast, setForecast] = useState([]) // predicción de la demanda
  const [topics, setTopics] = useState([])

  useEffect(() => {
    client.get('/dashboard/summary').then((r) => setSummary(r.data))
    client.get('/dashboard/demand-series').then((r) => setDemand(r.data.series))
    client.get('/dashboard/supply-series').then((r) => setSupply(r.data.series))
    client.get('/dashboard/demand-forecast?months=6').then((r) => setForecast(r.data.series))
    client.get('/analysis/topics?num_topics=5').then((r) => setTopics(r.data.topics))
  }, [])

  const PALETTE = ['#2563eb', '#16a34a', '#f59e0b', '#8b5cf6', '#ef4444', '#0ea5e9']

  const lineData = (series) =>
    series.map((s) => ({
      x: s.periods, y: s.values, type: 'scatter', mode: 'lines', name: s.category,
      line: { width: 2 },
    }))

  // Demanda media por área (interés 0-100), escala comparable entre áreas
  const demandComparison = [...demand]
    .map((s) => ({
      category: s.category,
      avg: s.values.length
        ? Math.round(s.values.reduce((a, b) => a + b, 0) / s.values.length)
        : 0,
    }))
    .sort((a, b) => b.avg - a.avg)

  return (
    <div className="container">
      <h1 className="page-title">Panel de análisis de demanda de cursos</h1>
      <p className="page-sub">Visión conjunta de la oferta y la demanda de formación en línea por área de conocimiento.</p>

      {/* --- KPIs --- */}
      <div className="cards">
        <Kpi icon="📚" bg="#eaf1ff" value={summary?.total_courses ?? '—'} label="Registros analizados" />
        <Kpi icon="🗂️" bg="#e7f7ee" value={summary?.total_categories ?? '—'} label="Áreas de conocimiento" />
        <Kpi icon="👥" bg="#fff4e5" value={summary ? summary.total_students.toLocaleString() : '—'} label="Estudiantes (acumulado)" />
        <Kpi icon="🗓️" bg="#f3e8ff" value={summary?.num_periods ?? '—'} label="Periodos con datos" />
      </div>

      {/* --- DEMANDA --- */}
      <div className="panel">
        <h3>Demanda de búsqueda por área</h3>
        <p className="subtitle">Índice de interés real de Google Trends (0–100), 2021–2026. Es la evolución de la demanda.</p>
        {demand.length > 0 ? (
          <Plot
            data={lineData(demand)}
            layout={{ ...chartLayout, yaxis: { ...chartLayout.yaxis, title: 'Interés (0-100)' } }}
            style={{ width: '100%', height: '420px' }}
            config={{ responsive: true, displaylogo: false }}
            useResizeHandler
          />
        ) : <p className="subtitle">Cargando…</p>}
      </div>

      {/* --- PREDICCIÓN DE LA DEMANDA (modelo predictivo básico) --- */}
      <div className="panel">
        <h3>Predicción de la demanda — proyección a 6 meses</h3>
        <p className="subtitle">Modelo predictivo básico (regresión lineal). Línea continua = histórico; línea punteada = previsión. Se muestran las 6 áreas de mayor demanda.</p>
        {forecast.length > 0 ? (
          <Plot
            data={forecast.slice(0, 6).flatMap((s, i) => {
              const color = PALETTE[i % PALETTE.length]
              return [
                { x: s.periods, y: s.values, type: 'scatter', mode: 'lines',
                  name: s.category, line: { color, width: 2 } },
                { x: [s.periods[s.periods.length - 1], ...s.forecast_periods],
                  y: [s.values[s.values.length - 1], ...s.forecast_values],
                  type: 'scatter', mode: 'lines', name: `${s.category} (previsión)`,
                  line: { color, width: 2, dash: 'dot' }, showlegend: false },
              ]
            })}
            layout={{ ...chartLayout, yaxis: { ...chartLayout.yaxis, title: 'Interés (0-100)' } }}
            style={{ width: '100%', height: '420px' }}
            config={{ responsive: true, displaylogo: false }}
            useResizeHandler
          />
        ) : <p className="subtitle">Cargando…</p>}
      </div>

      {/* --- OFERTA --- */}
      <div className="panel">
        <h3>Oferta de cursos publicados por área</h3>
        <p className="subtitle">Nº de cursos publicados por mes (Udemy, dato real con fecha), 2011–2017.</p>
        {supply.length > 0 ? (
          <Plot
            data={lineData(supply)}
            layout={{ ...chartLayout, yaxis: { ...chartLayout.yaxis, title: 'Nº de cursos' } }}
            style={{ width: '100%', height: '380px' }}
            config={{ responsive: true, displaylogo: false }}
            useResizeHandler
          />
        ) : <p className="subtitle">Cargando…</p>}
      </div>

      {/* --- Comparación de áreas (demanda media) --- */}
      <div className="panel">
        <h3>Comparación de áreas — demanda media de búsqueda</h3>
        <p className="subtitle">Interés medio de búsqueda (0–100) por área. Escala comparable.</p>
        {demandComparison.length > 0 ? (
          <Plot
            data={[{
              x: demandComparison.map((d) => d.avg).reverse(),
              y: demandComparison.map((d) => d.category).reverse(),
              type: 'bar',
              orientation: 'h',
              marker: { color: '#2563eb' },
              text: demandComparison.map((d) => d.avg).reverse(),
              textposition: 'auto',
            }]}
            layout={{ ...chartLayout, margin: { t: 20, r: 20, b: 40, l: 180 },
                      xaxis: { ...chartLayout.xaxis, title: 'Interés medio (0-100)' } }}
            style={{ width: '100%', height: '420px' }}
            config={{ responsive: true, displaylogo: false }}
            useResizeHandler
          />
        ) : <p className="subtitle">Cargando…</p>}
      </div>

      {/* --- Tendencias destacadas --- */}
      <div className="panel">
        <h3>Áreas con mayor crecimiento</h3>
        <p className="subtitle">Tendencia de la demanda de búsqueda por área.</p>
        <table>
          <thead>
            <tr><th>Área</th><th>Tendencia</th><th>Crecimiento</th><th>Confianza (R²)</th></tr>
          </thead>
          <tbody>
            {summary?.top_growing?.map((t) => (
              <tr key={t.category}>
                <td>{t.category}</td>
                <td><span className={`badge ${t.direction}`}>{t.direction}</span></td>
                <td>{t.growth_rate != null ? `${t.growth_rate}%` : '—'}</td>
                <td>{t.confidence_level != null ? t.confidence_level : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* --- Tópicos (LDA) --- */}
      <div className="panel">
        <h3>Temas latentes en las descripciones de los cursos</h3>
        <p className="subtitle">Minería de texto con modelado de tópicos (LDA).</p>
        {topics.length > 0 ? (
          <div className="topic-grid">
            {topics.map((t) => (
              <div key={t.topic} className="topic">
                <div className="tnum">Tópico {t.topic}</div>
                <div className="tkw">{t.keywords.slice(0, 6).join(', ')}</div>
              </div>
            ))}
          </div>
        ) : <p className="subtitle">Sin datos suficientes para el análisis de tópicos.</p>}
      </div>
    </div>
  )
}
