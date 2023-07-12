import React from 'react';

function TablaRegistros({ registros, editarRegistro, eliminarRegistro }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Paciente</th>
          <th>Azúcar</th>
          <th>Grasa</th>
          <th>Oxígeno</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {registros.map((registro) => (
          <tr key={registro.id}>
            <td>{registro.paciente}</td>
            <td>{registro.azucar}</td>
            <td>{registro.grasa}</td>
            <td>{registro.oxigeno}</td>
            <td>
              <button onClick={() => editarRegistro(registro.id)}>Editar</button>
              <button onClick={() => eliminarRegistro(registro.id)}>Eliminar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default TablaRegistros;
