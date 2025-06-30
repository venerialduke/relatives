import { useEffect, useState } from 'react'

const BACKEND_URL = 'http://127.0.0.1:5000'

function App() {
	const [system, setSystem] = useState(null)
	const [unit, setUnit] = useState(null)
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		async function fetchData() {
			const systemRes = await fetch(`${BACKEND_URL}/api/system`)
			const unitRes = await fetch(`${BACKEND_URL}/api/unit`)
			setSystem(await systemRes.json())
			setUnit(await unitRes.json())
			setLoading(false)
		}
		fetchData()
	}, [])

	const moveUnit = async (spaceId) => {
		await fetch(`${BACKEND_URL}/api/move_unit`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ space_id: spaceId }),
		})
		const res = await fetch(`${BACKEND_URL}/api/unit`)
		setUnit(await res.json())
	}

	const collectItem = async (item) => {
		await fetch(`${BACKEND_URL}/api/collect_item`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ item }),
		})
		const unitRes = await fetch(`${BACKEND_URL}/api/unit`)
		const systemRes = await fetch(`${BACKEND_URL}/api/system`)
		setUnit(await unitRes.json())
		setSystem(await systemRes.json())
	}

	if (loading) return <p>Loading system...</p>

	return (
		<div style={{ padding: '1rem', fontFamily: 'Arial, sans-serif' }}>
			<h1>{system.name}</h1>

			{system.bodies.map(body => (
				<div key={body.id} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
					<h2>{body.name}</h2>
					<ul>
						{body.spaces.map(space => {
							const isHere = space.id === unit.current_space_id
							return (
								<li key={space.id}>
									<span style={{ fontWeight: isHere ? 'bold' : 'normal' }}>
										{space.name}
									</span>
									{isHere && <span> 🚀 (Here)</span>}
									{!isHere && (
										<button onClick={() => moveUnit(space.id)} style={{ marginLeft: '10px' }}>
											Move Here
										</button>
									)}
									{isHere && space.items.length > 0 && (
										<ul>
											{space.items.map(item => (
												<li key={item}>
													{item}
													<button onClick={() => collectItem(item)} style={{ marginLeft: '10px' }}>
														Collect
													</button>
												</li>
											))}
										</ul>
									)}
								</li>
							)
						})}
					</ul>
				</div>
			))}

			<h3>Inventory:</h3>
			<ul>
				{unit.inventory.length === 0 ? (
					<li>Empty</li>
				) : (
					unit.inventory.map((item, i) => <li key={i}>{item}</li>)
				)}
			</ul>
		</div>
	)
}

export default App
