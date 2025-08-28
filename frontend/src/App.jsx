import React, { useState } from "react";
import axios from "axios";
import { Toaster, toast } from "react-hot-toast";

export default function App() {
  const [texto, setTexto] = useState("");
  const [resultados, setResultados] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [copiadoIndex, setCopiadoIndex] = useState(null);

  const buscar = async () => {
    if (!texto.trim()) {
      toast.error("Por favor, descreva sua necessidade técnica!");
      return;
    }
    setCarregando(true);
    try {
      const res = await axios.post("http://localhost:8000/recomendar", { texto });
      setResultados(res.data.recomendados);
    } catch (error) {
      console.error("Erro ao buscar:", error);
      toast.error("Erro ao buscar produtos. Tente novamente.");
    } finally {
      setCarregando(false);
    }
  };

  const copiarFichaCompleta = async (produto, idx) => {
    const fichaTexto = `Nome: ${produto.nome}
Descrição: ${produto.desc}
Detalhes:
- ${produto.detalhes.join("\n- ")}`.trim();
    try {
      await navigator.clipboard.writeText(fichaTexto);
      setCopiadoIndex(idx);
      setTimeout(() => setCopiadoIndex(null), 1500);
      toast.success("Ficha copiada para a área de transferência!");
    } catch (err) {
      console.error("Erro ao copiar:", err);
      toast.error("Erro ao copiar ficha.");
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            fontFamily: "Helvetica, Arial, sans-serif",
            borderRadius: "999px",
            background: "#fff",
            color: "#1e3a8a",
            border: "1px solid #cbd5e1",
          },
        }}
      />
      <header className="w-full h-[70px] bg-white border-b border-gray-200 flex items-center px-6">
        <img src="/advantech-logo.png" alt="Logo Advantech" className="h-[25px]" />
      </header>
      <main className="flex-grow p-10">
        <h1 className="text-3xl font-bold mb-4 tracking-wide text-center" style={{ fontFamily: 'Arial, sans-serif', color: 'white' }}>
          Advantech
        </h1>
        <h2 className="text-center text-xl text-white mb-8" style={{ fontFamily: 'Arial, sans-serif' }}>
          Digite sua demanda e veja os produtos compatíveis
        </h2>
        <input
          className="border border-gray-300 p-4 rounded-full max-w-6xl w-full shadow-sm focus:outline-none focus:ring-0 mx-auto block"
          placeholder="Ex: Tipo de processador, portas, energia, montagem, etc."
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <button
          onClick={buscar}
          className="mt-5 bg-white text-blue-800 font-medium px-4 py-2 rounded-full mx-auto block w-48 shadow-md hover:bg-blue-100 hover:shadow-xl transition duration-200"
          style={{ fontFamily: "Helvetica, Arial, sans-serif" }}
        >
          Buscar Produtos
        </button>

        {carregando && (
          <div className="flex justify-center items-center mt-10">
            <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-600"></div>
          </div>
        )}

        {!carregando && resultados.length > 0 && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
            {resultados.map((prod, idx) => (
              <div key={idx} className="bg-white p-4 rounded shadow">
                <h2 className="text-lg font-bold">{prod.nome}</h2>
                <p className="text-gray-600 mb-2">{prod.desc}</p>
                <ul className="mt-2 mb-2 text-sm list-disc list-inside text-gray-700">
                  {prod.detalhes.map((d, i) => <li key={i}>{d}</li>)}
                </ul>
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => copiarFichaCompleta(prod, idx)}
                    className="text-sm bg-white text-blue-800 font-medium px-3 py-1.5 rounded-full shadow hover:bg-blue-100 hover:shadow-lg transition duration-200"
                    style={{ fontFamily: "Helvetica, Arial, sans-serif" }}
                  >
                    {copiadoIndex === idx ? "Ficha copiada!" : "Copiar Ficha"}
                  </button>
                  <button
                    onClick={() => window.open(prod.product_url, "_blank")}
                    className="text-sm bg-blue-800 text-white font-medium px-3 py-1.5 rounded-full shadow hover:bg-blue-700 hover:shadow-lg transition duration-200"
                  >
                    Ir para página do produto
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
      <footer className="bg-gray-100 text-center text-sm text-gray-600 py-4 border-t">
        • 2025 •  <span className="text-blue-800 font-medium">Advantech</span>
      </footer>
    </div>
  );
}