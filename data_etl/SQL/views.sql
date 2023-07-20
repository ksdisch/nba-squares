-- View player's first and last names (players) along with their yearly stats (player_yearly_stats) --
CREATE VIEW player_avg_view AS
SELECT pystats.id, pystats.player_id, players.first_name, players.last_name, pystats.year, pystats.age, pystats.pos, pystats.g, pystats.gs, pystats.mp_per_g, pystats.fg_per_g, pystats.fga_per_g, pystats.fg_pct, pystats.fg3_per_g, pystats.fg3a_per_g, pystats.fg3_pct, pystats.fg2_per_g, pystats.fg2a_per_g, pystats.fg2_pct, pystats.efg_pct, pystats.ft_per_g, pystats.fta_per_g, pystats.ft_pct, pystats.orb_per_g, pystats.drb_per_g, pystats.trb_per_g, pystats.ast_per_g, pystats.stl_per_g, pystats.blk_per_g, pystats.tov_per_g, pystats.pf_per_g, pystats.pts_per_g
FROM player_yearly_stats AS pystats
JOIN players ON players.id = pystats.player_id
ORDER BY pystats.id DESC; 

-- View award vote receiving player's first and last names (players) along with the award they received votes for, and the rank they finished that year in the voting --
CREATE VIEW player_award_view AS
SELECT pav.id, pav.player_id, players.first_name, players.last_name, pav.year, pav.award_name, pav.rank, pys.age, pys.pos, pys.g, pys.mp_per_g, pys.pts_per_g, pys.ast_per_g, pys.trb_per_g, pys.blk_per_g, pys.stl_per_g, pys.fg_pct, pys.fg3_pct, pys.ft_pct, pys.efg_pct, pys.ft_per_g, pys.orb_per_g, pys.drb_per_g,pys.tov_per_g
FROM players_awards AS pav
JOIN players ON players.id = pav.player_id
JOIN player_yearly_stats AS pys ON pys.player_id = pav.player_id AND pys.year = pav.year
ORDER BY pav.id DESC;

