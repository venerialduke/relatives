import React from "react";

function ResourceList({ title, resources }) {
  return (
    <div>
      <h4>{title}</h4>
      {resources && Object.keys(resources).length > 0 ? (
        <ul>
          {Object.entries(resources).map(([name, count]) => (
            <li key={name}>{name}: {count}</li>
          ))}
        </ul>
      ) : (
        <p>None</p>
      )}
    </div>
  );
}

export default ResourceList;