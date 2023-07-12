import React, { useState, useEffect } from 'react';
import ApiService from './ApiService';
import './App.css';
function App() {
const [data, setData] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await ApiService.get('/paciente/sangre_evaluada');
      setData(response.data.registros); // Acceder a la propiedad 'registros' de la respuesta
    } catch (error) {
      console.error('Error al obtener los registros:', error);
    }
  };
  
  const editarRegistro = (id) => {
    console.log('Editar registro con ID:', id);
    // Implementa la lógica para editar el registro con el ID proporcionado
  };

  const eliminarRegistro = async (paciente) => {
    try {
      // Envía la solicitud DELETE al endpoint correspondiente de la API para eliminar el registro por nombre
      await ApiService.delete(`/paciente/sangre_evaluada/${paciente}`);
      console.log('Registro eliminado:', paciente);
      // Actualiza la lista de registros después de eliminar uno
      fetchData();
    } catch (error) {
      console.error('Error al eliminar el registro:', error);
    }
  };
  
  const agregarRegistro = () => {
    console.log('Agregar nuevo registro');
    // Implementa la lógica para agregar un nuevo registro
  };
  return (
    <div className="container">
      <h1>Registros</h1>
      <div className="button-container">
        <button className="button" onClick={agregarRegistro}>Agregar Registro</button>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Paciente</th>
            <th>Azúcar</th>
            <th>Grasa</th>
            <th>Oxígeno</th>
            <th>Riesgo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {data.map((registro) => (
            <tr key={registro.paciente}>
              <td>{registro.paciente}</td>
              <td>{registro.azucar}</td>
              <td>{registro.grasa}</td>
              <td>{registro.oxigeno}</td>
              <td>{registro.riesgo}</td>
              <td className="actions">
                <button className="button" onClick={() => editarRegistro(registro.id)}>Editar</button>
                <button className="button" onClick={() => eliminarRegistro(registro.paciente)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;