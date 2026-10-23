const assert = require('node:assert/strict');
const test = require('node:test');

const experience = require('../source/js/map-experience');

function paper(id, date) {
  return { id, title: id, date, url: `/article/${id}/` };
}

const payload = {
  meta: { generated: '2026-10-23T00:00:00Z' },
  places: [
    {
      id: 'beijing::school', name: 'Beijing', city: 'Beijing', location_type: 'school',
      wgs84: [116.4, 39.9], image: '/images/map/beijing.webp',
      city_images: ['/images/map/beijing.webp', '/images/map/beijing-2.webp'],
      institutions: [{ name: 'Tsinghua University', description: 'School' }],
      papers: [paper('bj-school', '2026-09-01')]
    },
    {
      id: 'beijing::company', name: 'Beijing', city: 'Beijing', location_type: 'company',
      wgs84: [116.3, 40.0], image: '/images/map/beijing.webp',
      city_images: ['/images/map/beijing.webp'],
      institutions: [{ name: 'ByteDance', description: 'Company' }],
      papers: [paper('bj-company', '2026-08-01'), paper('bj-school', '2026-09-01')]
    },
    {
      id: 'singapore::school', name: 'Singapore', city: 'Singapore', location_type: 'school',
      wgs84: [103.8, 1.35], image: '/images/map/singapore.webp', city_images: [],
      institutions: [{ name: 'National University of Singapore', description: 'School' }],
      papers: [paper('sg-paper', '2026-10-01')]
    },
    {
      id: 'boston::school', name: 'Boston', city: 'Boston', location_type: 'school',
      wgs84: [-71.05, 42.36], image: '/images/map/boston.webp', city_images: [],
      institutions: [{ name: 'MIT', description: 'School' }, { name: 'Harvard', description: 'School' }],
      papers: [paper('boston-a', '2026-10-15'), paper('boston-b', '2026-09-15')]
    }
  ]
};

test('core research cities stay first without borrowing papers for empty cities', () => {
  const cities = experience.buildResearchCities(payload, {
    now: '2026-10-23T00:00:00Z', limit: 6
  });

  assert.deepEqual(cities.slice(0, 4).map(city => city.key), [
    'beijing', 'hangzhou', 'singapore', 'new-york'
  ]);
  assert.equal(cities.find(city => city.key === 'beijing').paperCount, 2);
  assert.equal(cities.find(city => city.key === 'beijing').institutionCount, 2);
  assert.equal(cities.find(city => city.key === 'new-york').paperCount, 0);
  assert.deepEqual(cities.find(city => city.key === 'new-york').papers, []);
});

test('data-driven city candidates are ranked by recent papers and institutions', () => {
  const cities = experience.buildResearchCities(payload, {
    now: '2026-10-23T00:00:00Z', limit: 5
  });

  assert.equal(cities[4].key, 'boston');
  assert.equal(cities[4].paperCount, 2);
  assert.equal(cities[4].institutionCount, 2);
  assert.equal(cities[4].isCore, false);
});

test('city aggregation keeps unique papers, institutions, and images', () => {
  const cities = experience.aggregatePayloadCities(payload);
  const beijing = cities.find(city => city.key === 'beijing');

  assert.deepEqual(beijing.papers.map(item => item.id), ['bj-school', 'bj-company']);
  assert.deepEqual(beijing.institutions.map(item => item.name), ['Tsinghua University', 'ByteDance']);
  assert.deepEqual(beijing.city_images, ['/images/map/beijing.webp', '/images/map/beijing-2.webp']);
});

test('arrival plans use curated core cameras and deterministic generated cameras', () => {
  const core = experience.buildArrivalPlan({ key: 'beijing', center: [116.4, 39.9] });
  const generatedA = experience.buildArrivalPlan({ key: 'boston', center: [-71.05, 42.36] });
  const generatedB = experience.buildArrivalPlan({ key: 'boston', center: [-71.05, 42.36] });

  assert.equal(core.length, 2);
  assert.deepEqual(core[1].center, [116.4074, 39.9042]);
  assert.equal(core[1].exaggeration, 1.42);
  assert.deepEqual(generatedA, generatedB);
  assert.equal(generatedA[1].center[0], -71.05);
  assert.equal(generatedA[1].center[1], 42.36);
});
