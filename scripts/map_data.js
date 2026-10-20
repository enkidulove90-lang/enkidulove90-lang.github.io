/* Build-time paper map payload. Coordinates are WGS-84 for Leaflet/OSM. */

const fs = require('node:fs');
const path = require('node:path');

function cityKey(value) {
  return String(value || '').trim().toLocaleLowerCase('en-US');
}

function validPlace(place) {
  return place && place.id && place.name && Array.isArray(place.wgs84) && place.wgs84.length === 2 &&
    place.wgs84.every(Number.isFinite) && /^\/images\/map\//.test(String(place.image || ''));
}

function expectsVenueCity(post) {
  const type = String(post.venue_type || '').trim().toLocaleLowerCase('en-US');
  return Boolean(String(post.venue_city || '').trim()) || type.includes('会议') || type.includes('conference');
}

function isPaper(post) {
  const type = String(post.venue_type || '').trim().toLocaleLowerCase('en-US');
  return !type.includes('随笔') && !type.includes('essay');
}

function paperKeys(post) {
  const pathValue = String(post.path || '').replace(/^\//, '').replace(/\/$/, '');
  return [post.slug, pathValue, pathValue.split('/').pop(), post.title].filter(Boolean).map(String);
}

function cleanDescription(value) {
  return String(value || '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/^#{1,6}\s+.*$/gm, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/[*_`]/g, '')
    .replace(/\s+/g, ' ').trim();
}

function articleIntroduction(post) {
  const explicit = post.description || post.excerpt;
  if (explicit) return cleanDescription(explicit);
  const markdown = String(post._content || post.__source_text || '').replace(/^---[\s\S]*?---\s*/, '');
  const paragraph = markdown.split(/\r?\n\s*\r?\n/)
    .map(block => block.trim())
    .find(block => block.length >= 20 && !/^(?:>|#{1,6}\s|!\[|[-*+]\s|\|)/.test(block));
  if (paragraph) return cleanDescription(paragraph);
  const html = String(post.content || post.raw || '');
  const paragraphs = Array.from(html.matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/gi), match => cleanDescription(match[1]));
  return paragraphs.find(text => text.length >= 20 && !/^论文[:：]/.test(text)) || cleanDescription(html);
}

function serializePaper(post) {
  const plainDescription = articleIntroduction(post);
  return {
    id: String(post.slug || post.path || post.title || ''),
    title: String(post.title || ''),
    date: post.date && typeof post.date.format === 'function' ? post.date.format('YYYY-MM-DD') : String(post.date || ''),
    url: '/' + String(post.path || '').replace(/^\//, ''),
    venue_name: String(post.venue_name || ''),
    description: plainDescription,
    arxiv_id: String(post.arxiv_id || '')
  };
}

function canonicalPaperIdentity(post) {
  const source = [post.arxiv_id, post.paper_url, post.source_url, post.slug, post.path].filter(Boolean).join(' ');
  const arxiv = source.match(/(?:arxiv\.org\/(?:abs|pdf)\/|paper-)?(\d{4}\.\d{4,5})(?:v\d+)?/i);
  return arxiv ? 'arxiv:' + arxiv[1] : 'slug:' + String(post.slug || post.path || post.title || '').toLocaleLowerCase('en-US');
}

function buildMapPayload(posts, places, threshold = 0.6, assignments = []) {
  const allSourcePosts = Array.from(posts || []);
  const seenPapers = new Set();
  const sourcePosts = allSourcePosts.filter(post => {
    const identity = canonicalPaperIdentity(post);
    if (seenPapers.has(identity)) return false;
    seenPapers.add(identity);
    return true;
  });
  const paperPosts = sourcePosts.filter(isPaper);
  const validPlaces = Array.from(places || []).filter(validPlace);
  const byCity = new Map();
  validPlaces.forEach(place => {
    byCity.set(cityKey(place.name), place);
    byCity.set(cityKey(place.id), place);
  });
  const assignmentByPaper = new Map();
  Array.from(assignments || []).forEach(assignment => assignmentByPaper.set(String(assignment.paper_id), assignment));
  const resolvedForPost = new Map();
  sourcePosts.forEach(post => {
    const assignment = paperKeys(post).map(key => assignmentByPaper.get(key)).find(Boolean);
    if (assignment) resolvedForPost.set(post, assignment);
  });

  const eligiblePosts = sourcePosts.filter(post => expectsVenueCity(post) || resolvedForPost.has(post));
  const groupedPlaces = new Map();
  const locatedPosts = new Set();
  const physicalLocatedPosts = new Set();
  const papers = sourcePosts.map(post => {
    const assignment = resolvedForPost.get(post);
    let place = assignment
      ? validPlaces.find(candidate => candidate.id === assignment.place_id)
      : byCity.get(cityKey(post.venue_city));
    if (!place) return null;
    locatedPosts.add(post);
    const locationType = String((assignment && assignment.location_type) || 'venue').toLowerCase();
    if (locationType !== 'virtual') physicalLocatedPosts.add(post);
    const cityId = cityKey(place.city || place.name).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || place.id;
    const groupId = cityId + '::' + locationType;
    if (!groupedPlaces.has(groupId)) {
      groupedPlaces.set(groupId, {
        ...place,
        id: groupId,
        base_place_id: place.id,
        location_type: locationType,
        hover_image: place.hover_image || place.image,
        hover_text: place.hover_text || place.description || place.name,
        city_images: Array.from(new Set([...(place.city_images || []), place.image].filter(Boolean))),
        institutions: [],
        papers: []
      });
    }
    const paper = {
      ...serializePaper(post),
      city_id: groupId,
      location_type: locationType,
      location_label: String((assignment && assignment.location_label) || post.venue_name || place.name),
      location_source: String((assignment && assignment.source) || 'venue_city')
    };
    const group = groupedPlaces.get(groupId);
    group.city_images = Array.from(new Set([...group.city_images, ...(place.city_images || []), place.image].filter(Boolean)));
    const institution = place.institution || {
      name: paper.location_label,
      kind: locationType,
      description: `${paper.location_label} 位于 ${place.city || place.name}。`
    };
    if (institution.name && !group.institutions.some(item => item.name === institution.name)) {
      group.institutions.push(institution);
    }
    group.papers.push(paper);
    return paper;
  }).filter(Boolean).sort((a, b) => b.date.localeCompare(a.date));

  groupedPlaces.forEach(place => place.papers.sort((a, b) => b.date.localeCompare(a.date)));

  const unlocated = paperPosts.filter(post => !physicalLocatedPosts.has(post)).map(post => ({
    ...serializePaper(post),
    reason: '尚无经过验证的机构或会议坐标'
  })).sort((a, b) => b.date.localeCompare(a.date));
  const coveredEligible = eligiblePosts.filter(post => physicalLocatedPosts.has(post)).length;
  const coverage = eligiblePosts.length ? coveredEligible / eligiblePosts.length : 0;
  return {
    meta: {
      generated: new Date().toISOString(),
      total_papers: sourcePosts.length,
      duplicate_papers: allSourcePosts.length - sourcePosts.length,
      library_papers: paperPosts.length,
      eligible_papers: eligiblePosts.length,
      located_papers: physicalLocatedPosts.size,
      mapped_papers: papers.length,
      physical_located_papers: physicalLocatedPosts.size,
      virtual_unlocated_papers: papers.filter(paper => paper.location_type === 'virtual').length,
      unlocated_papers: unlocated.length,
      city_count: new Set(Array.from(groupedPlaces.values())
        .filter(place => place.location_type !== 'virtual')
        .map(place => cityKey(place.city || place.name))).size,
      covered_eligible_papers: coveredEligible,
      coverage,
      threshold,
      enabled: eligiblePosts.length > 0 && coverage >= threshold
    },
    places: Array.from(groupedPlaces.values()),
    papers,
    unlocated,
    links: papers.map(paper => ({ paper_id: paper.id, city_id: paper.city_id, type: paper.location_type }))
  };
}

function registerGenerator(instance) {
  instance.extend.generator.register('paper_map_data', function generatePaperMap(locals) {
    const data = locals.data && (locals.data.places || locals.data['places']) || {};
    const places = Array.isArray(data) ? data : (data.places || []);
    const assignments = Array.isArray(data.assignments) ? data.assignments : [];
    const posts = locals.posts && typeof locals.posts.toArray === 'function' ? locals.posts.toArray() : Array.from(locals.posts || []);
    posts.forEach(post => {
      if (post.description || post.excerpt || post.content || post._content) return;
      const sourcePath = post.full_source || (post.source && path.join(instance.source_dir, post.source));
      if (sourcePath && fs.existsSync(sourcePath)) post.__source_text = fs.readFileSync(sourcePath, 'utf8');
    });
    return [{ path: 'map_data.json', data: JSON.stringify(buildMapPayload(posts, places, 0.6, assignments)) }];
  });
}

if (typeof hexo !== 'undefined') registerGenerator(hexo);

module.exports = { buildMapPayload, registerGenerator };
