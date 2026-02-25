"use client";

import { useState, useEffect } from "react";

interface Recommendation {
  name: string;
  full_address: string;
  rating: string;
  price_for_two: string;
  recommendation_reason: string;
}

interface AIResponse {
  recommendations: Recommendation[];
  summary: string;
}

export default function Home() {
  // Option lists
  const [locations, setLocations] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);

  // State
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedPriceRange, setSelectedPriceRange] = useState("");
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([]);
  const [minRating, setMinRating] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AIResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showValidation, setShowValidation] = useState(false);

  // Custom Dropdown states
  const [locationSearch, setLocationSearch] = useState("");
  const [isLocationOpen, setIsLocationOpen] = useState(false);
  const [cuisineSearch, setCuisineSearch] = useState("");
  const [isCuisineOpen, setIsCuisineOpen] = useState(false);

  // Custom Dropdown states for Price and Rating
  const [isPriceOpen, setIsPriceOpen] = useState(false);
  const [isRatingOpen, setIsRatingOpen] = useState(false);

  // Fetch options
  useEffect(() => {
    async function init() {
      try {
        const [locRes, cuiRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/locations"),
          fetch("http://127.0.0.1:8000/api/cuisines")
        ]);
        if (locRes.ok) setLocations(await locRes.json());
        if (cuiRes.ok) setCuisines(await cuiRes.json());
      } catch (err) {
        console.error("Initialization failed", err);
      }
    }
    init();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLocation || !selectedPriceRange) {
      setShowValidation(true);
      return;
    }

    setShowValidation(false);
    setLoading(true);
    setError(null);
    setResults(null);

    const payload = {
      location: selectedLocation,
      price_range: selectedPriceRange,
      cuisines: selectedCuisines.length > 0 ? selectedCuisines : null,
      min_rating: parseFloat(minRating) || null,
      limit: 15
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("The network is serving someone else right now. Try again.");
      }

      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleCuisine = (c: string) => {
    if (selectedCuisines.includes(c)) {
      setSelectedCuisines(selectedCuisines.filter(item => item !== c));
    } else {
      setSelectedCuisines([...selectedCuisines, c]);
    }
    setCuisineSearch("");
    setIsCuisineOpen(false);
  };

  const filteredLocations = locations.filter(loc =>
    loc.toLowerCase().includes(locationSearch.toLowerCase())
  );

  const filteredCuisines = cuisines.filter(c =>
    c.toLowerCase().includes(cuisineSearch.toLowerCase()) &&
    !selectedCuisines.includes(c)
  );

  return (
    <main className="main-container">
      {/* Visual Background Orbs & Bokeh */}
      <div className="bg-orbs">
        <div className="orb orb-red"></div>
        <div className="orb orb-amber"></div>
        <div className="bokeh bokeh-1"></div>
        <div className="bokeh bokeh-2"></div>
        <div className="bokeh bokeh-3"></div>
      </div>

      <header className="text-center">
        <h1 className="main-heading">Zomato AI Restaurant Recommendation</h1>
        <p className="sub-heading">
          Find the best places to eat in <span className="highlight-city">Bangalore</span>
        </p>
      </header>

      <section className="form-panel glass-card">
        <form onSubmit={handleSearch}>
          <div className="control-grid">
            {/* Location (Custom Combobox) */}
            <div className="control-group">
              <div className="label-box">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                Where are you looking for? *
              </div>
              <div className="dropdown-container">
                <input
                  className="input-style"
                  placeholder="Search locality..."
                  value={isLocationOpen ? locationSearch : selectedLocation}
                  onFocus={() => {
                    setIsLocationOpen(true);
                    setLocationSearch("");
                  }}
                  onClick={() => {
                    setIsLocationOpen(true);
                    setLocationSearch("");
                  }}
                  onChange={(e) => {
                    const val = e.target.value;
                    setLocationSearch(val);
                    if (val === "") setSelectedLocation("");
                  }}
                  onBlur={() => setTimeout(() => setIsLocationOpen(false), 200)}
                  autoComplete="off"
                />
                <div className="dropdown-icon" onClick={() => setIsLocationOpen(!isLocationOpen)}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m6 9 6 6 6-6" /></svg>
                </div>
                {isLocationOpen && (
                  <div className="custom-dropdown-list">
                    {filteredLocations.map(loc => (
                      <div
                        key={loc}
                        className={`dropdown-item ${selectedLocation === loc ? 'selected' : ''}`}
                        onMouseDown={(e) => {
                          e.preventDefault();
                          setSelectedLocation(loc);
                          setLocationSearch(loc);
                          setIsLocationOpen(false);
                        }}
                      >
                        {loc}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Price (Custom Glass Dropdown) */}
            <div className="control-group">
              <div className="label-box">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                Price range *
              </div>
              <div className="dropdown-container">
                <div
                  className="input-style"
                  onClick={() => setIsPriceOpen(true)}
                  onFocus={() => setIsPriceOpen(true)}
                  tabIndex={0}
                  onBlur={() => setTimeout(() => setIsPriceOpen(false), 200)}
                >
                  {selectedPriceRange || "Select range"}
                </div>
                <div className="dropdown-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m6 9 6 6 6-6" /></svg>
                </div>
                {isPriceOpen && (
                  <div className="custom-dropdown-list">
                    {["Under ₹500", "₹500 - ₹1500", "Above ₹1500"].map(range => (
                      <div
                        key={range}
                        className={`dropdown-item ${selectedPriceRange === range ? 'selected' : ''}`}
                        onClick={() => {
                          setSelectedPriceRange(range);
                          setIsPriceOpen(false);
                        }}
                      >
                        {range}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Cuisines (Multi-select) */}
            <div className="control-group">
              <div className="label-box">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>
                Cuisines (optional)
              </div>
              <div className="dropdown-container">
                <div className="tag-input-wrapper" onClick={() => {
                  document.getElementById('cuisine-input')?.focus();
                  setCuisineSearch("");
                  setIsCuisineOpen(true);
                }}>
                  {selectedCuisines.map(c => (
                    <div key={c} className="chip">
                      {c} <span className="chip-close" onClick={(e) => { e.stopPropagation(); toggleCuisine(c); }}>×</span>
                    </div>
                  ))}
                  <input
                    id="cuisine-input"
                    placeholder={selectedCuisines.length === 0 ? "Select cuisine(s)..." : ""}
                    value={cuisineSearch}
                    onFocus={() => {
                      setIsCuisineOpen(true);
                      setCuisineSearch("");
                    }}
                    onChange={(e) => setCuisineSearch(e.target.value)}
                    onBlur={() => setTimeout(() => setIsCuisineOpen(false), 200)}
                    autoComplete="off"
                  />
                  <div className="dropdown-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m6 9 6 6 6-6" /></svg>
                  </div>
                </div>
                {/* Dropdown list - Anchored downward by default */}
                {isCuisineOpen && filteredCuisines.length > 0 && (
                  <div className="custom-dropdown-list">
                    {filteredCuisines.map(c => (
                      <div key={c} className="dropdown-item" onClick={() => toggleCuisine(c)}>{c}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Min Rating (Custom Glass Dropdown) */}
            <div className="control-group">
              <div className="label-box">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffb703" strokeWidth="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                Min Rating (optional)
              </div>
              <div className="dropdown-container">
                <div
                  className="input-style"
                  onClick={() => setIsRatingOpen(true)}
                  onFocus={() => setIsRatingOpen(true)}
                  tabIndex={0}
                  onBlur={() => setTimeout(() => setIsRatingOpen(false), 200)}
                >
                  {minRating ? `${minRating}+` : "Any"}
                </div>
                <div className="dropdown-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m6 9 6 6 6-6" /></svg>
                </div>
                {isRatingOpen && (
                  <div className="custom-dropdown-list">
                    {[
                      { val: "", label: "Any" },
                      { val: "3.5", label: "3.5+" },
                      { val: "4.0", label: "4.0+" },
                      { val: "4.5", label: "4.5+" }
                    ].map(opt => (
                      <div
                        key={opt.val}
                        className={`dropdown-item ${minRating === opt.val ? 'selected' : ''}`}
                        onClick={() => {
                          setMinRating(opt.val);
                          setIsRatingOpen(false);
                        }}
                      >
                        {opt.label}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
          <button type="submit" className="search-trigger" disabled={loading}>Get Expert Picks ✨</button>
          {showValidation && <div className="validation-bubble">For best result fill the required field</div>}
        </form>
      </section>

      {/* Loading */}
      {loading && (
        <div className="loading-orbit">
          <div className="orbit-circle"></div>
          <p className="loading-label">Hold on we are finding the best match for you</p>
        </div>
      )}

      {/* Results */}
      {results && (
        <section className="results-area animate-fade-in">
          <div className="expert-summary-box glass-card">
            <strong>Expert Summary:</strong> {results.summary}
          </div>

          {results.recommendations.length > 0 && (
            <>
              <h2>Here is the best Picks for you</h2>
              {results.recommendations.map((rec, i) => (
                <div key={rec.name + i} className="rec-item glass-card">
                  <div className="rec-title-row">
                    <h3 className="rec-name">{rec.name}</h3>
                    <div className="rating-pill">★ {rec.rating}</div>
                  </div>
                  <div className="address-line">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                    {rec.full_address}
                  </div>
                  <div className="price-tag">{rec.price_for_two} for two</div>
                  <div className="expert-reason">{rec.recommendation_reason}</div>
                </div>
              ))}
            </>
          )}
        </section>
      )}
    </main>
  );
}
