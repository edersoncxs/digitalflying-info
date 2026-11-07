<?php
// Endpoint PRÓPRIO da Digital Flying para os apps mandarem e-mail (sem depender de serviço de terceiros).
// Publicar em https://digitalflying.com.br/app/contato.php e, no digitalflying.json, trocar:
//   "envio": { "email": "https://digitalflying.com.br/app/contato.php", "chave": "" }
// A senha do e-mail fica SÓ aqui no servidor da Digital Flying (config abaixo), nunca nos apps.
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
$CONFIG = [
    'para' => 'ederson.cxs@gmail.com',
    'smtp' => ['host' => 'mail.digitalflying.com.br', 'porta' => 465, 'usuario' => 'apps@digitalflying.com.br', 'senha' => 'TROCAR'],
    'limite_por_hora' => 20, // por IP, contra abuso
];
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit('{"success":false}'); }
$d = json_decode((string)file_get_contents('php://input'), true) ?: [];
$msg = trim((string)($d['message'] ?? ''));
if (mb_strlen($msg) < 3 || mb_strlen($msg) > 8000) { http_response_code(400); exit('{"success":false,"message":"Mensagem inválida."}'); }
// limite simples por IP
$f = sys_get_temp_dir() . '/dfcontato-' . md5($_SERVER['REMOTE_ADDR'] ?? '') . '-' . date('YmdH');
$n = (int)@file_get_contents($f) + 1; @file_put_contents($f, (string)$n);
if ($n > $CONFIG['limite_por_hora']) { http_response_code(429); exit('{"success":false,"message":"Muitas mensagens. Tente mais tarde."}'); }
$assunto = mb_substr(trim((string)($d['subject'] ?? 'Contato pelo app')), 0, 150);
$nome = mb_substr(trim((string)($d['from_name'] ?? 'App')), 0, 80);
$responder = filter_var($d['email'] ?? '', FILTER_VALIDATE_EMAIL) ?: '';
// Envio: mail() da hospedagem (ou troque por SMTP com $CONFIG['smtp'] — mesmo cliente SMTP do DF Delivery: nucleo/email.php)
$cab = "From: =?UTF-8?B?" . base64_encode("$nome via apps") . "?= <{$CONFIG['smtp']['usuario']}>\r\nContent-Type: text/plain; charset=UTF-8\r\n" . ($responder ? "Reply-To: $responder\r\n" : '');
$ok = mail($CONFIG['para'], '=?UTF-8?B?' . base64_encode($assunto) . '?=', $msg, $cab);
echo json_encode(['success' => $ok]);
