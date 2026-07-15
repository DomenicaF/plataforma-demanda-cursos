import { useEffect, useState } from 'react'
import client from '../api/client'

// Administración de fuentes de datos (RF-01/CU-01) y ejecución del ETL (CU-02).
export default function Admin() {
  const [sources, setSources] = useState([])
  const [history, setHistory] = useState([])
  const [form, setForm] = useState({ name: '', source_type: 'csv', url: '' })
  const [msg, setMsg] = useState('')
  const [running, setRunning] = useState(false)

  const load = () => {
    client.get('/admin/sources').then((r) => setSources(r.data))
    client.get('/etl/history?limit=10').then((r) => setHistory(r.data))
  }
  useEffect(load, [])

  const createSource = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      await client.post('/admin/sources', form)
      setForm({ name: '', source_type: 'csv', url: '' })
      load()
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Error al crear la fuente')
    }
  }

  const remove = async (id) => {
    if (!confirm('¿Eliminar esta fuente de datos?')) return
    await client.delete(`/admin/sources/${id}`)
    load()
  }

  const runEtl = async (id) => {
    setRunning(true)
    setMsg('')
    try {
      const url = id ? `/etl/run?source_id=${id}` : '/etl/run'
      const { data } = await client.post(url)
      setMsg('ETL ejecutado: ' + JSON.stringify(data.ejecuciones))
      load()
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Error al ejecutar el ETL')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="container">
      <div className="panel">
        <h3>Fuentes de datos</h3>
        <table>
          <thead>
            <tr><th>ID</th><th>Nombre</th><th>Tipo</th><th>Activa</th><th>Última ejecución</th><th></th></tr>
          </thead>
          <tbody>
            {sources.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.source_type}</td>
                <td>{s.is_active ? 'Sí' : 'No'}</td>
                <td>{s.last_run_at ? new Date(s.last_run_at).toLocaleString() : '—'}</td>
                <td style={{ display: 'flex', gap: 8 }}>
                  <button className="secondary" disabled={running} onClick={() => runEtl(s.id)}>Ejecutar ETL</button>
                  <button className="danger" onClick={() => remove(s.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginTop: 12 }}>
          <button disabled={running} onClick={() => runEtl(null)}>
            {running ? 'Ejecutando…' : 'Ejecutar ETL de todas las fuentes activas'}
          </button>
        </div>
        {msg && <div className="hint">{msg}</div>}
      </div>

      <div className="panel">
        <h3>Registrar nueva fuente</h3>
        <form onSubmit={createSource} className="row">
          <div style={{ flex: 2 }}>
            <label className="label">Nombre</label>
            <input value={form.name} required
                   onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div style={{ flex: 1 }}>
            <label className="label">Tipo</label>
            <select value={form.source_type}
                    onChange={(e) => setForm({ ...form, source_type: e.target.value })}>
              <option value="csv">csv (dataset)</option>
              <option value="google_trends">google_trends (real)</option>
            </select>
          </div>
          <div style={{ flex: 2 }}>
            <label className="label">URL (opcional)</label>
            <input value={form.url}
                   onChange={(e) => setForm({ ...form, url: e.target.value })} />
          </div>
          <button type="submit">Registrar</button>
        </form>
      </div>

      <div className="panel">
        <h3>Historial de ejecuciones ETL</h3>
        <table>
          <thead>
            <tr><th>ID</th><th>Estado</th><th>Extraídos</th><th>Transformados</th><th>Cargados</th><th>Duración (s)</th><th>Inicio</th></tr>
          </thead>
          <tbody>
            {history.map((h) => (
              <tr key={h.id}>
                <td>{h.id}</td>
                <td><span className={`badge ${h.status}`}>{h.status}</span></td>
                <td>{h.records_extracted}</td>
                <td>{h.records_transformed}</td>
                <td>{h.records_loaded}</td>
                <td>{h.duration_seconds != null ? h.duration_seconds.toFixed(2) : '—'}</td>
                <td>{h.started_at ? new Date(h.started_at).toLocaleString() : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
