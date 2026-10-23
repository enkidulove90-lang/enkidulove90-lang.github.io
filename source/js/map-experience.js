(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.PaperMapExperience = api;
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';

  var CORE_CITY_PROFILES = [
    {
      key: 'beijing', name: '北京', aliases: ['beijing', '北京市'],
      center: [116.4074, 39.9042], approach: [115.72, 40.35],
      zoom: 8.2, pitch: 61, bearing: -18,
      geography: '燕山与华北平原之间的科研中枢'
    },
    {
      key: 'hangzhou', name: '杭州', aliases: ['hangzhou', '杭州市'],
      center: [120.1551, 30.2741], approach: [119.48, 29.86],
      zoom: 8.7, pitch: 62, bearing: 24,
      geography: '东南丘陵与钱塘江湾交汇的产业研究城市'
    },
    {
      key: 'singapore', name: '新加坡', aliases: ['singapore', '新加坡'],
      center: [103.8198, 1.3521], approach: [103.25, 1.02],
      zoom: 9.2, pitch: 60, bearing: -28,
      geography: '海峡、岛屿与国际研究网络连接之地'
    },
    {
      key: 'new-york', name: '纽约', aliases: ['new york', 'new york city', '纽约'],
      center: [-74.006, 40.7128], approach: [-74.72, 40.22],
      zoom: 8.8, pitch: 62, bearing: 20,
      geography: '大西洋海岸与哈德逊河口的全球创新节点'
    }
  ];

  function normalizeCityKey(value) {
    return String(value || '')
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim()
      .toLocaleLowerCase('en-US')
      .replace(/[^a-z0-9\u3400-\u9fff]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  function profileFor(value) {
    var normalized = normalizeCityKey(value);
    return CORE_CITY_PROFILES.find(function (profile) {
      return profile.key === normalized || profile.aliases.some(function (alias) {
        return normalizeCityKey(alias) === normalized;
      });
    }) || null;
  }

  function uniqueBy(items, identity) {
    var seen = new Set();
    return items.filter(function (item) {
      var key = identity(item);
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function paperIdentity(paper) {
    return String(paper.id || paper.url || paper.slug || paper.title || '').trim();
  }

  function aggregatePayloadCities(payload) {
    var byKey = new Map();
    Array.from((payload && payload.places) || []).forEach(function (place) {
      if (!place || place.location_type === 'virtual') return;
      var rawName = place.city || place.name || place.id;
      var profile = profileFor(rawName);
      var key = profile ? profile.key : normalizeCityKey(rawName);
      if (!key) return;
      if (!byKey.has(key)) {
        byKey.set(key, {
          key: key,
          name: profile ? profile.name : rawName,
          sourceName: rawName,
          center: profile ? profile.center.slice() : Array.from(place.wgs84 || [0, 0]),
          geography: profile ? profile.geography : String(place.description || ''),
          image: place.image || '',
          city_images: [], institutions: [], papers: [], places: [],
          isCore: Boolean(profile)
        });
      }
      var city = byKey.get(key);
      city.places.push(place);
      city.city_images = uniqueBy(city.city_images.concat(place.city_images || [], place.image || []), function (item) { return item; });
      city.institutions = uniqueBy(city.institutions.concat(place.institutions || [], place.institution || []), function (item) {
        return String(item && item.name || '').trim().toLocaleLowerCase('en-US');
      });
      city.papers = uniqueBy(city.papers.concat(place.papers || []), paperIdentity);
      if (!city.image && place.image) city.image = place.image;
    });
    return Array.from(byKey.values()).map(function (city) {
      city.papers.sort(function (left, right) { return String(right.date || '').localeCompare(String(left.date || '')); });
      city.paperCount = city.papers.length;
      city.institutionCount = city.institutions.length;
      city.latestDate = city.papers.length ? String(city.papers[0].date || '') : '';
      return city;
    });
  }

  function recentPaperCount(city, now) {
    var boundary = new Date(now || Date.now());
    if (Number.isNaN(boundary.getTime())) boundary = new Date();
    boundary.setUTCDate(boundary.getUTCDate() - 365);
    return city.papers.filter(function (paper) {
      var published = new Date(paper.date);
      return !Number.isNaN(published.getTime()) && published >= boundary;
    }).length;
  }

  function cityScore(city, now) {
    return city.paperCount * 10 + city.institutionCount * 4 + recentPaperCount(city, now) * 6;
  }

  function emptyCoreCity(profile) {
    return {
      key: profile.key, name: profile.name, sourceName: profile.name,
      center: profile.center.slice(), geography: profile.geography,
      image: '', city_images: [], institutions: [], papers: [], places: [],
      paperCount: 0, institutionCount: 0, latestDate: '', isCore: true, score: 0
    };
  }

  function buildResearchCities(payload, options) {
    var settings = options || {};
    var limit = Math.max(CORE_CITY_PROFILES.length, Number(settings.limit) || 8);
    var aggregated = aggregatePayloadCities(payload);
    var byKey = new Map(aggregated.map(function (city) { return [city.key, city]; }));
    var core = CORE_CITY_PROFILES.map(function (profile) {
      var city = byKey.get(profile.key) || emptyCoreCity(profile);
      return Object.assign({}, city, {
        name: profile.name,
        center: profile.center.slice(),
        geography: profile.geography,
        isCore: true,
        score: cityScore(city, settings.now)
      });
    });
    var dynamic = aggregated
      .filter(function (city) { return !CORE_CITY_PROFILES.some(function (profile) { return profile.key === city.key; }); })
      .map(function (city) { return Object.assign({}, city, { isCore: false, score: cityScore(city, settings.now) }); })
      .sort(function (left, right) {
        return right.score - left.score || right.latestDate.localeCompare(left.latestDate) || left.name.localeCompare(right.name);
      });
    return core.concat(dynamic).slice(0, limit);
  }

  function stableHash(value) {
    var hash = 0;
    String(value || '').split('').forEach(function (character) {
      hash = ((hash << 5) - hash + character.charCodeAt(0)) | 0;
    });
    return Math.abs(hash);
  }

  function buildArrivalPlan(city) {
    var profile = CORE_CITY_PROFILES.find(function (item) { return item.key === city.key; });
    var center = Array.from((profile && profile.center) || city.center || [0, 0]);
    var bearing = profile ? profile.bearing : (stableHash(city.key) % 70) - 35;
    var approach = profile
      ? profile.approach.slice()
      : [center[0] - 0.7, Math.max(-80, Math.min(80, center[1] + 0.45))];
    return [
      { center: approach, zoom: 5.2, pitch: 42, bearing: bearing * 0.45, duration: 900, exaggeration: 1.08 },
      {
        center: center,
        zoom: profile ? profile.zoom : 8.4,
        pitch: profile ? profile.pitch : 59,
        bearing: bearing,
        duration: 1500,
        exaggeration: 1.42
      }
    ];
  }

  return {
    CORE_CITY_PROFILES: CORE_CITY_PROFILES,
    normalizeCityKey: normalizeCityKey,
    aggregatePayloadCities: aggregatePayloadCities,
    buildResearchCities: buildResearchCities,
    buildArrivalPlan: buildArrivalPlan
  };
});
