#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use chrono::{DateTime, Datelike, Duration, Local, NaiveDate, Weekday};
use dirs::home_dir;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter};
use std::path::PathBuf;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Todo {
    pub id: String,
    pub text: String,
    pub completed: bool,
    pub created_at: String,
    pub deadline: Option<String>,
    pub tag_ids: Vec<String>,
    pub repeat_rule: Option<RepeatRule>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepeatRule {
    pub r#type: RepeatType,
    pub interval: u32,
    pub weekdays: Vec<u32>,
    pub end_date: Option<String>,
    pub last_generated: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum RepeatType {
    Daily,
    Weekly,
    Monthly,
    Yearly,
    Weekdays,
    Weekends,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tag {
    pub id: String,
    pub name: String,
    pub color: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub theme: String,
    pub is_transparent: bool,
    pub password: Option<String>,
    pub is_locked: bool,
    pub window_geometry: WindowGeometry,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowGeometry {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppData {
    pub todos: HashMap<String, Vec<Todo>>,
    pub tags: Vec<Tag>,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            theme: "light".to_string(),
            is_transparent: false,
            password: None,
            is_locked: false,
            window_geometry: WindowGeometry {
                x: 100,
                y: 100,
                width: 500,
                height: 550,
            },
        }
    }
}

impl Default for AppData {
    fn default() -> Self {
        Self {
            todos: HashMap::new(),
            tags: Vec::new(),
        }
    }
}

fn get_config_path() -> PathBuf {
    home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".cute_notes_config.json")
}

fn get_data_path() -> PathBuf {
    home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".cute_notes_data.json")
}

fn load_config() -> AppConfig {
    let path = get_config_path();
    if path.exists() {
        if let Ok(file) = File::open(&path) {
            let reader = BufReader::new(file);
            if let Ok(config) = serde_json::from_reader(reader) {
                return config;
            }
        }
    }
    AppConfig::default()
}

fn save_config(config: &AppConfig) -> Result<(), String> {
    let path = get_config_path();
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(&path)
        .map_err(|e| e.to_string())?;
    let writer = BufWriter::new(file);
    serde_json::to_writer_pretty(writer, config).map_err(|e| e.to_string())?;
    Ok(())
}

fn load_data() -> AppData {
    let path = get_data_path();
    if path.exists() {
        if let Ok(file) = File::open(&path) {
            let reader = BufReader::new(file);
            if let Ok(data) = serde_json::from_reader(reader) {
                return data;
            }
        }
    }
    AppData::default()
}

fn save_data(data: &AppData) -> Result<(), String> {
    let path = get_data_path();
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(&path)
        .map_err(|e| e.to_string())?;
    let writer = BufWriter::new(file);
    serde_json::to_writer_pretty(writer, data).map_err(|e| e.to_string())?;
    Ok(())
}

fn generate_uuid() -> String {
    Uuid::new_v4().to_string()
}

fn today_str() -> String {
    Local::now().format("%Y-%m-%d").to_string()
}

fn parse_date(date_str: &str) -> Option<NaiveDate> {
    NaiveDate::parse_from_str(date_str, "%Y-%m-%d").ok()
}

fn format_date(date: NaiveDate) -> String {
    date.format("%Y-%m-%d").to_string()
}

#[tauri::command]
fn get_config() -> AppConfig {
    load_config()
}

#[tauri::command]
fn set_theme(theme: String) -> Result<(), String> {
    let mut config = load_config();
    config.theme = theme;
    save_config(&config)
}

#[tauri::command]
fn set_transparent(is_transparent: bool) -> Result<(), String> {
    let mut config = load_config();
    config.is_transparent = is_transparent;
    save_config(&config)
}

#[tauri::command]
fn set_password(password: String) -> Result<(), String> {
    let mut config = load_config();
    config.password = Some(password);
    save_config(&config)
}

#[tauri::command]
fn check_password(password: String) -> bool {
    let config = load_config();
    config.password == Some(password)
}

#[tauri::command]
fn has_password() -> bool {
    let config = load_config();
    config.password.is_some()
}

#[tauri::command]
fn set_locked(is_locked: bool) -> Result<(), String> {
    let mut config = load_config();
    config.is_locked = is_locked;
    save_config(&config)
}

#[tauri::command]
fn set_window_geometry(x: i32, y: i32, width: u32, height: u32) -> Result<(), String> {
    let mut config = load_config();
    config.window_geometry = WindowGeometry { x, y, width, height };
    save_config(&config)
}

#[tauri::command]
fn get_todos(date_str: String) -> Vec<Todo> {
    let data = load_data();
    data.todos.get(&date_str).cloned().unwrap_or_default()
}

#[tauri::command]
fn add_todo(
    date_str: String,
    text: String,
    deadline: Option<String>,
    tag_ids: Option<Vec<String>>,
    repeat_rule: Option<RepeatRule>,
) -> Result<Todo, String> {
    let mut data = load_data();
    
    let todo = Todo {
        id: generate_uuid(),
        text,
        completed: false,
        created_at: Local::now().to_rfc3339(),
        deadline,
        tag_ids: tag_ids.unwrap_or_default(),
        repeat_rule,
    };
    
    let todos = data.todos.entry(date_str).or_default();
    todos.push(todo.clone());
    
    save_data(&data)?;
    Ok(todo)
}

#[tauri::command]
fn update_todo(
    date_str: String,
    todo_id: String,
    text: Option<String>,
    completed: Option<bool>,
    deadline: Option<String>,
    tag_ids: Option<Vec<String>>,
    repeat_rule: Option<RepeatRule>,
) -> Result<bool, String> {
    let mut data = load_data();
    
    if let Some(todos) = data.todos.get_mut(&date_str) {
        for todo in todos {
            if todo.id == todo_id {
                if let Some(t) = text {
                    todo.text = t;
                }
                if let Some(c) = completed {
                    todo.completed = c;
                }
                if deadline.is_some() {
                    todo.deadline = deadline;
                }
                if let Some(tags) = tag_ids {
                    todo.tag_ids = tags;
                }
                if repeat_rule.is_some() {
                    todo.repeat_rule = repeat_rule;
                }
                
                save_data(&data)?;
                return Ok(true);
            }
        }
    }
    
    Ok(false)
}

#[tauri::command]
fn delete_todo(date_str: String, todo_id: String) -> Result<bool, String> {
    let mut data = load_data();
    
    let mut should_remove = false;
    let mut changed = false;
    
    if let Some(todos) = data.todos.get_mut(&date_str) {
        let original_len = todos.len();
        todos.retain(|t| t.id != todo_id);
        changed = todos.len() != original_len;
        should_remove = todos.is_empty();
    }
    
    if should_remove {
        data.todos.remove(&date_str);
    }
    
    if changed {
        save_data(&data)?;
        Ok(true)
    } else {
        Ok(false)
    }
}

#[tauri::command]
fn search_todos(keyword: Option<String>, tag_ids: Option<Vec<String>>) -> Vec<serde_json::Value> {
    let data = load_data();
    let mut results = Vec::new();
    
    for (date_str, todos) in &data.todos {
        for todo in todos {
            let mut text_match = true;
            let mut tag_match = true;
            
            if let Some(ref kw) = keyword {
                if !todo.text.to_lowercase().contains(&kw.to_lowercase()) {
                    text_match = false;
                }
            }
            
            if let Some(ref tags) = tag_ids {
                if !tags.is_empty() {
                    tag_match = tags.iter().all(|tag_id| todo.tag_ids.contains(tag_id));
                }
            }
            
            if text_match && tag_match {
                results.push(serde_json::json!({
                    "date": date_str,
                    "todo": todo
                }));
            }
        }
    }
    
    results
}

#[tauri::command]
fn get_all_tags() -> Vec<Tag> {
    let data = load_data();
    data.tags
}

#[tauri::command]
fn add_tag(name: String) -> Result<Tag, String> {
    let mut data = load_data();
    
    if data.tags.iter().any(|t| t.name == name) {
        return Err("标签已存在".to_string());
    }
    
    let tag = Tag {
        id: generate_uuid(),
        name,
        color: "#FFD700".to_string(),
    };
    
    data.tags.push(tag.clone());
    save_data(&data)?;
    Ok(tag)
}

#[tauri::command]
fn update_tag(tag_id: String, new_name: String) -> Result<bool, String> {
    let mut data = load_data();
    
    for tag in &mut data.tags {
        if tag.id == tag_id {
            tag.name = new_name;
            save_data(&data)?;
            return Ok(true);
        }
    }
    
    Ok(false)
}

#[tauri::command]
fn delete_tag(tag_id: String) -> Result<bool, String> {
    let mut data = load_data();
    let original_len = data.tags.len();
    
    data.tags.retain(|t| t.id != tag_id);
    
    for todos in data.todos.values_mut() {
        for todo in todos {
            todo.tag_ids.retain(|id| id != &tag_id);
        }
    }
    
    if data.tags.len() != original_len {
        save_data(&data)?;
        Ok(true)
    } else {
        Ok(false)
    }
}

#[tauri::command]
fn get_tag(tag_id: String) -> Option<Tag> {
    let data = load_data();
    data.tags.into_iter().find(|t| t.id == tag_id)
}

fn is_task_urgent(todo: &Todo, hours: i64) -> bool {
    if todo.completed {
        return false;
    }
    
    let deadline = match &todo.deadline {
        Some(d) => {
            match DateTime::parse_from_rfc3339(d) {
                Ok(dt) => dt,
                Err(_) => return false,
            }
        }
        None => return false,
    };
    
    let now = Local::now();
    let cutoff = now + Duration::hours(hours);
    
    now <= deadline && deadline <= cutoff
}

#[tauri::command]
fn get_urgent_todos(hours: Option<i64>) -> Vec<serde_json::Value> {
    let data = load_data();
    let hours = hours.unwrap_or(3);
    let mut urgent = Vec::new();
    
    for (date_str, todos) in &data.todos {
        for todo in todos {
            if is_task_urgent(todo, hours) {
                urgent.push(serde_json::json!({
                    "date": date_str,
                    "todo": todo,
                    "deadline": todo.deadline
                }));
            }
        }
    }
    
    urgent.sort_by(|a, b| {
        let a_deadline = a["deadline"].as_str().unwrap_or("");
        let b_deadline = b["deadline"].as_str().unwrap_or("");
        a_deadline.cmp(b_deadline)
    });
    
    urgent
}

fn calculate_next_repeat_date(current_date_str: &str, rule: &RepeatRule) -> Option<String> {
    let current_date = parse_date(current_date_str)?;
    
    if let Some(end_date_str) = &rule.end_date {
        let end_date = parse_date(end_date_str)?;
        if current_date > end_date {
            return None;
        }
    }
    
    let next_date = match rule.r#type {
        RepeatType::Daily => current_date + Duration::days(rule.interval as i64),
        RepeatType::Weekly => {
            if rule.weekdays.is_empty() {
                current_date + Duration::weeks(rule.interval as i64)
            } else {
                let today_weekday = current_date.weekday().num_days_from_monday();
                let mut sorted_weekdays = rule.weekdays.clone();
                sorted_weekdays.sort();
                
                let mut next = None;
                for &wd in &sorted_weekdays {
                    if wd > today_weekday {
                        let days_to_add = (wd - today_weekday) as i64;
                        next = Some(current_date + Duration::days(days_to_add));
                        break;
                    }
                }
                
                if next.is_none() {
                    let days_to_next_week = (7 - today_weekday + sorted_weekdays[0]) as i64;
                    next = Some(current_date + Duration::days(days_to_next_week));
                }
                
                let mut next_date = next?;
                if rule.interval > 1 {
                    next_date = next_date + Duration::weeks((rule.interval - 1) as i64);
                }
                next_date
            }
        }
        RepeatType::Weekdays => {
            let mut next = current_date + Duration::days(1);
            while next.weekday() == Weekday::Sat || next.weekday() == Weekday::Sun {
                next = next + Duration::days(1);
            }
            next
        }
        RepeatType::Weekends => {
            let mut next = current_date + Duration::days(1);
            while next.weekday() != Weekday::Sat && next.weekday() != Weekday::Sun {
                next = next + Duration::days(1);
            }
            next
        }
        RepeatType::Monthly => {
            let mut year = current_date.year();
            let mut month = current_date.month() + rule.interval;
            
            while month > 12 {
                month -= 12;
                year += 1;
            }
            
            let day = current_date.day();
            let max_day = match month {
                1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
                4 | 6 | 9 | 11 => 30,
                2 => {
                    if (year % 4 == 0 && year % 100 != 0) || year % 400 == 0 {
                        29
                    } else {
                        28
                    }
                }
                _ => 31,
            };
            
            let day = std::cmp::min(day, max_day);
            NaiveDate::from_ymd_opt(year, month, day)?
        }
        RepeatType::Yearly => {
            let year = current_date.year() + rule.interval as i32;
            let month = current_date.month();
            let day = current_date.day();
            
            let max_day = if month == 2 {
                if (year % 4 == 0 && year % 100 != 0) || year % 400 == 0 {
                    29
                } else {
                    28
                }
            } else {
                match month {
                    1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
                    4 | 6 | 9 | 11 => 30,
                    _ => 31,
                }
            };
            
            let day = std::cmp::min(day, max_day);
            NaiveDate::from_ymd_opt(year, month, day)?
        }
    };
    
    if let Some(end_date_str) = &rule.end_date {
        let end_date = parse_date(end_date_str)?;
        if next_date > end_date {
            return None;
        }
    }
    
    Some(format_date(next_date))
}

#[tauri::command]
fn generate_repeat_todos() -> Result<u32, String> {
    let mut data = load_data();
    let today = today_str();
    let mut generated_count = 0;
    
    let todos_copy = data.todos.clone();
    
    for (date_str, todos) in &todos_copy {
        for todo in todos {
            let rule = match &todo.repeat_rule {
                Some(r) => r,
                None => continue,
            };
            
            if let Some(last_gen) = &rule.last_generated {
                if last_gen >= &today {
                    continue;
                }
            }
            
            let mut next_date = calculate_next_repeat_date(date_str, rule);
            
            while let Some(ref nd) = next_date {
                if nd > &today {
                    break;
                }
                
                let existing_todos = data.todos.get(nd).cloned().unwrap_or_default();
                let todo_exists = existing_todos.iter().any(|t| {
                    t.text == todo.text
                        && t.repeat_rule.is_some()
                        && t.repeat_rule.as_ref().unwrap().r#type == rule.r#type
                });
                
                if !todo_exists {
                    let new_todo = Todo {
                        id: generate_uuid(),
                        text: todo.text.clone(),
                        completed: false,
                        created_at: Local::now().to_rfc3339(),
                        deadline: todo.deadline.clone(),
                        tag_ids: todo.tag_ids.clone(),
                        repeat_rule: Some(rule.clone()),
                    };
                    
                    data.todos.entry(nd.clone()).or_default().push(new_todo);
                    generated_count += 1;
                }
                
                for todos in data.todos.values_mut() {
                    for t in todos {
                        if let Some(ref mut r) = t.repeat_rule {
                            if r.r#type == rule.r#type
                                && r.interval == rule.interval
                                && r.weekdays == rule.weekdays
                            {
                                r.last_generated = Some(nd.clone());
                            }
                        }
                    }
                }
                
                next_date = calculate_next_repeat_date(nd, rule);
            }
        }
    }
    
    save_data(&data)?;
    Ok(generated_count)
}

#[tauri::command]
fn get_today() -> String {
    today_str()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            get_config,
            set_theme,
            set_transparent,
            set_password,
            check_password,
            has_password,
            set_locked,
            set_window_geometry,
            get_todos,
            add_todo,
            update_todo,
            delete_todo,
            search_todos,
            get_all_tags,
            add_tag,
            update_tag,
            delete_tag,
            get_tag,
            get_urgent_todos,
            generate_repeat_todos,
            get_today,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
