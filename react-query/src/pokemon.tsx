import { useEffect, useState } from "react";

const getPokemon = async () => {
  const response = await fetch("https://pokeapi.co/api/v2/pokemon?limit=10");
  const data = await response.json();
  return data.results;
};

type Pokemon = {
  name: string;
  url: string;
};

const PokeList = () => {
  const [pokemon, setPokemon] = useState<Pokemon[]>([]);

  useEffect(() => {
    const fetchdata = async () => {
      const response = await getPokemon();
      setPokemon(response);
    };

    if (pokemon.length === 0) {
      fetchdata();
    }
  }, [pokemon]);

  return (
    <>
      <button>Refetch</button>
      <ul>
        {pokemon.map((item) => (
          <li key={item.name}>{item.name}</li>
        ))}
      </ul>
    </>
  );
};

export default PokeList;
