import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [tipoErro, setTipoErro] = useState('none');
  const [qubit, setQubit] = useState(0);
  const [shots, setShots] = useState(1024);
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [imagem, setImagem] = useState(null);

  const executarSimulacao = async () => {
    setCarregando(true);
    setResultado(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/quantum/simulate`, {
        error: { type: tipoErro, qubit },
        shots
      });
      setResultado(response.data);
    } catch (error) {
      alert('❌ Error: Backend is not running!');
    }
    setCarregando(false);
  };

  const gerarCircuito = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/quantum/circuit?error_type=${tipoErro}&error_qubit=${qubit}`
      );
      setImagem(response.data.circuit_image);
    } catch (error) {
      alert('❌ Error generating circuit');
    }
  };

  const interpretarResultado = (resultadoStr) => {
    const partes = resultadoStr.split(' ');
    if (partes.length < 3) return { fase: 'unknown', bit: 'unknown' };
    
    const fase = partes[1];
    const bit = partes[2];
    
    const faseTexto = {
      '00': '✅ No phase error',
      '01': '🟡 Phase error in Block 0',
      '10': '🟡 Phase error in Block 2',
      '11': '🟡 Phase error in Block 1'
    }[fase] || '⚠️ Unknown';
    
    const bitTexto = {
    // Block 0 (bits 0-1) - qubits 0,1,2
    '000001': '🔴 Bit-Flip error in Qubit 0',
    '000011': '🔴 Bit-Flip error in Qubit 1',
    '000010': '🔴 Bit-Flip error in Qubit 2',
    
    // Block 1 (bits 2-3) - qubits 3,4,5
    '000100': '🔴 Bit-Flip error in Qubit 3',
    '001100': '🔴 Bit-Flip error in Qubit 4',
    '001000': '🔴 Bit-Flip error in Qubit 5',
    
    // Block 2 (bits 4-5) - qubits 6,7,8
    '010000': '🔴 Bit-Flip error in Qubit 6',
    '110000': '🔴 Bit-Flip error in Qubit 7',
    '100000': '🔴 Bit-Flip error in Qubit 8',
    
    '000000': '✅ No Bit-Flip error'
    }[bit] || '⚠️ Unknown';
    
    return { fase: faseTexto, bit: bitTexto };
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.titulo}>🛡️ Quantum Shor Simulator</h1>
      <p style={styles.subtitulo}>9-qubit error correction code</p>

      <div style={styles.card}>
        <div style={styles.campo}>
          <label style={styles.label}>Error Type:</label>
          <select 
            value={tipoErro} 
            onChange={(e) => setTipoErro(e.target.value)}
            style={styles.select}
          >
            <option value="none">🔵 No Error</option>
            <option value="x">❌ Bit-flip (X)</option>
            <option value="z">🟡 Phase-flip (Z)</option>
            <option value="y">🔴 Both (Y)</option>
          </select>
        </div>

        <div style={styles.campo}>
          <label style={styles.label}>Qubit:</label>
          <select 
            value={qubit} 
            onChange={(e) => setQubit(Number(e.target.value))}
            style={styles.select}
          >
            {[0,1,2,3,4,5,6,7,8].map(i => (
              <option key={i} value={i}>Qubit {i}</option>
            ))}
          </select>
        </div>

        <div style={styles.campo}>
          <label style={styles.label}>Shots: {shots}</label>
          <input 
            type="range" 
            min="10" 
            max="10000" 
            step="10"
            value={shots} 
            onChange={(e) => setShots(Number(e.target.value))}
            style={styles.range}
          />
        </div>

        <div style={styles.botoes}>
          <button 
            onClick={executarSimulacao} 
            disabled={carregando}
            style={carregando ? styles.botaoDesabilitado : styles.botaoPrimario}
          >
            {carregando ? '⏳ Running...' : '🚀 Execute'}
          </button>
          <button 
            onClick={gerarCircuito}
            style={styles.botaoSecundario}
          >
            🔬 Generate Circuit
          </button>
        </div>
      </div>

      {resultado && (
        <div style={styles.card}>
          <h2 style={styles.subtituloCard}>📊 Result</h2>
          <p><strong>Logical state:</strong> |{resultado.logical_state}⟩</p>
          <p><strong>Operations:</strong> {resultado.circuit_size}</p>
          
          {Object.entries(resultado.counts).map(([chave, valor]) => {
            const interpretacao = interpretarResultado(chave);
            return (
              <div key={chave} style={styles.itemResultado}>
                <div style={styles.cabecalhoResultado}>
                  <code style={styles.codigo}>{chave}</code>
                  <span style={styles.badge}>{valor} runs</span>
                </div>
                <div style={styles.interpretacao}>
                  <div>• {interpretacao.fase}</div>
                  <div>• {interpretacao.bit}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {imagem && (
        <div style={styles.card}>
          <h2 style={styles.subtituloCard}>🔬 Quantum Circuit</h2>
          <img 
            src={`data:image/png;base64,${imagem}`} 
            style={styles.imagem}
            alt="Quantum circuit"
          />
        </div>
      )}

      <div style={styles.status}>
        ✅ Backend: http://localhost:8000
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 700,
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh'
  },
  titulo: {
    color: '#4f46e5',
    marginBottom: '5px',
    fontSize: '28px'
  },
  subtitulo: {
    color: '#666',
    marginBottom: '30px',
    fontSize: '16px'
  },
  subtituloCard: {
    marginTop: '0',
    marginBottom: '20px',
    color: '#333',
    fontSize: '20px'
  },
  card: {
    backgroundColor: '#fff',
    padding: '25px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    marginBottom: '20px'
  },
  campo: {
    marginBottom: '20px'
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '600',
    color: '#333'
  },
  select: {
    width: '100%',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #ddd',
    fontSize: '14px'
  },
  range: {
    width: '100%'
  },
  botoes: {
    display: 'flex',
    gap: '10px',
    marginTop: '10px'
  },
  botaoPrimario: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#4f46e5',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600'
  },
  botaoSecundario: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#6b7280',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600'
  },
  botaoDesabilitado: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#a5b4fc',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'not-allowed',
    fontSize: '16px',
    fontWeight: '600'
  },
  itemResultado: {
    backgroundColor: '#f9fafb',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '10px',
    border: '1px solid #e5e7eb'
  },
  cabecalhoResultado: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px'
  },
  codigo: {
    fontFamily: 'monospace',
    fontWeight: 'bold'
  },
  badge: {
    backgroundColor: '#e5e7eb',
    padding: '2px 10px',
    borderRadius: '12px',
    fontSize: '14px'
  },
  interpretacao: {
    fontSize: '14px',
    color: '#4b5563'
  },
  imagem: {
    maxWidth: '100%',
    height: 'auto',
    border: '1px solid #e5e7eb',
    borderRadius: '8px'
  },
  status: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#ecfdf5',
    borderRadius: '8px',
    color: '#059669',
    fontWeight: '500'
  }
};