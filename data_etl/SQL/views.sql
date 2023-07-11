-- View player's first and last names (players) along with their yearly stats (player_yearly_stats) --
CREATE VIEW player_avg_view AS
SELECT pystats.id, pystats.player_id, players.first_name, players.last_name, pystats.year, pystats.pts_per_g, pystats.ast_per_g, pystats.trb_per_g, pystats.stl_per_g, pystats.blk_per_g, pystats.fg_pct, pystats.fg3_pct, pystats.ft_pct 
FROM player_yearly_stats AS pystats
JOIN players ON players.id = pystats.player_id
ORDER BY pystats.id DESC; 




-- 
-- 'id', 'player_id', 'year', 'age', 'pos', 'g', 'gs', 'mp_per_g', pystats.pts_per_g, pystats.ast_per_g, pystats.treb_per_g 


-- 'fg_per_g', 'fga_per_g', 'fg_pct', 'fg3_per_g', 'fg3a_per_g', 'fg3_pct', 'fg2_per_g', 'fg2a_per_g', 'fg2_pct', 'efg_pct', 'ft_per_g', 'fta_per_g', 'ft_pct', 'orb_per_g', 'drb_per_g', 'trb_per_g', 'ast_per_g', 'stl_per_g', 'blk_per_g', 'tov_per_g', 'pf_per_g'