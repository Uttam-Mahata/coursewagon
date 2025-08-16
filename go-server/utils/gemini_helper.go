package utils

import (
	"context"
	"encoding/json"
	"fmt"
	"go-server/models"
	"os"
	"regexp"
	"strings"

	"github.com/sirupsen/logrus"
	"google.golang.org/genai"
)

type GeminiHelper struct {
	client   *genai.Client
	apiKey   string
	modelName string
}

// NewGeminiHelper creates a new Gemini helper instance
func NewGeminiHelper() *GeminiHelper {
	apiKey := os.Getenv("API_KEY")
	if apiKey == "" {
		logrus.Warning("No API_KEY found in environment variables. Gemini functionality will not work.")
		return &GeminiHelper{apiKey: ""}
	}

	return &GeminiHelper{
		apiKey:    apiKey,
		modelName: "gemini-2.5-flash", // Default model
	}
}

// InitClient initializes the Gemini client
func (gh *GeminiHelper) InitClient(ctx context.Context) error {
	if gh.apiKey == "" {
		return fmt.Errorf("no API key available for Gemini")
	}

	client, err := genai.NewClient(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to create Gemini client: %w", err)
	}

	gh.client = client
	return nil
}

// GenerateContent generates content using Gemini API
func (gh *GeminiHelper) GenerateContent(ctx context.Context, prompt string) (string, error) {
	if err := gh.InitClient(ctx); err != nil {
		return "", err
	}
	defer gh.client.Close()

	result, err := gh.client.Models.GenerateContent(
		ctx,
		gh.modelName,
		genai.Text(prompt),
		nil,
	)
	if err != nil {
		logrus.Errorf("Error generating content: %v", err)
		return "", err
	}

	return result.Text(), nil
}

// GenerateContentWithThinking generates content with thinking disabled
func (gh *GeminiHelper) GenerateContentWithThinking(ctx context.Context, prompt string, disableThinking bool) (string, error) {
	if err := gh.InitClient(ctx); err != nil {
		return "", err
	}
	defer gh.client.Close()

	var config *genai.GenerateContentConfig
	if disableThinking {
		config = &genai.GenerateContentConfig{
			ThinkingConfig: &genai.ThinkingConfig{
				ThinkingBudget: int32(0), // Disables thinking
			},
		}
	}

	result, err := gh.client.Models.GenerateContent(
		ctx,
		gh.modelName,
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating content with thinking: %v", err)
		return "", err
	}

	return result.Text(), nil
}

// GenerateContentWithSystemInstruction generates content with system instructions
func (gh *GeminiHelper) GenerateContentWithSystemInstruction(ctx context.Context, prompt, systemInstruction string) (string, error) {
	if err := gh.InitClient(ctx); err != nil {
		return "", err
	}
	defer gh.client.Close()

	config := &genai.GenerateContentConfig{
		SystemInstruction: genai.NewContentFromText(systemInstruction, genai.RoleUser),
	}

	result, err := gh.client.Models.GenerateContent(
		ctx,
		gh.modelName,
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating content with system instruction: %v", err)
		return "", err
	}

	return result.Text(), nil
}

// GenerateStructuredOutput generates JSON output using response schema
func (gh *GeminiHelper) GenerateStructuredOutput(ctx context.Context, prompt string, schema *genai.Schema) (string, error) {
	if err := gh.InitClient(ctx); err != nil {
		return "", err
	}
	defer gh.client.Close()

	config := &genai.GenerateContentConfig{
		ResponseMIMEType: "application/json",
		ResponseSchema:   schema,
	}

	result, err := gh.client.Models.GenerateContent(
		ctx,
		gh.modelName,
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating structured output: %v", err)
		return "", err
	}

	return result.Text(), nil
}

// GenerateSubjects generates subjects for a course using structured output
func (gh *GeminiHelper) GenerateSubjects(ctx context.Context, courseName, courseDescription string) ([]string, error) {
	prompt := fmt.Sprintf(`
Generate a comprehensive list of subjects for the course "%s" with description: "%s".
Provide 5-8 core subjects that would be essential for this course.
Return only the subject names as a JSON array.
`, courseName, courseDescription)

	schema := &genai.Schema{
		Type: genai.TypeArray,
		Items: &genai.Schema{
			Type: genai.TypeString,
		},
	}

	result, err := gh.GenerateStructuredOutput(ctx, prompt, schema)
	if err != nil {
		return nil, err
	}

	var subjects []string
	if err := json.Unmarshal([]byte(result), &subjects); err != nil {
		logrus.Errorf("Error unmarshaling subjects: %v", err)
		return nil, err
	}

	return subjects, nil
}

// GenerateChapters generates chapters for a subject using structured output
func (gh *GeminiHelper) GenerateChapters(ctx context.Context, subjectName, courseName string) ([]string, error) {
	prompt := fmt.Sprintf(`
Generate a comprehensive list of chapters for the subject "%s" in the course "%s".
Provide 6-10 logical chapters that would cover this subject thoroughly.
Return only the chapter names as a JSON array.
`, subjectName, courseName)

	schema := &genai.Schema{
		Type: genai.TypeArray,
		Items: &genai.Schema{
			Type: genai.TypeString,
		},
	}

	result, err := gh.GenerateStructuredOutput(ctx, prompt, schema)
	if err != nil {
		return nil, err
	}

	var chapters []string
	if err := json.Unmarshal([]byte(result), &chapters); err != nil {
		logrus.Errorf("Error unmarshaling chapters: %v", err)
		return nil, err
	}

	return chapters, nil
}

// GenerateTopics generates topics for a chapter using structured output
func (gh *GeminiHelper) GenerateTopics(ctx context.Context, chapterName, subjectName, courseName string) ([]string, error) {
	prompt := fmt.Sprintf(`
Generate a comprehensive list of topics for the chapter "%s" in subject "%s" for the course "%s".
Provide 5-8 specific topics that would be covered in this chapter.
Return only the topic names as a JSON array.
`, chapterName, subjectName, courseName)

	schema := &genai.Schema{
		Type: genai.TypeArray,
		Items: &genai.Schema{
			Type: genai.TypeString,
		},
	}

	result, err := gh.GenerateStructuredOutput(ctx, prompt, schema)
	if err != nil {
		return nil, err
	}

	var topics []string
	if err := json.Unmarshal([]byte(result), &topics); err != nil {
		logrus.Errorf("Error unmarshaling topics: %v", err)
		return nil, err
	}

	return topics, nil
}

// GenerateTopicContent generates detailed content for a topic
func (gh *GeminiHelper) GenerateTopicContent(ctx context.Context, topicName, chapterName, subjectName, courseName string) (string, error) {
	prompt := fmt.Sprintf(`
Generate detailed, in-depth content as well as a tutorial for the topic "%s", under the chapter "%s",
under the subject "%s" for the course "%s".

The content should adhere to the following detailed approach:

1. **Introduction**: Start with a clear and engaging introduction that outlines what will be covered in this topic.

2. **Core Concepts**: Break down the topic into fundamental concepts, explaining each with clear definitions and examples.

3. **Detailed Explanation**: Provide comprehensive explanations with:
   - Real-world examples and applications
   - Step-by-step processes where applicable
   - Common misconceptions and how to avoid them
   - Best practices and industry standards

4. **Practical Examples**: Include multiple practical examples that demonstrate the concepts in action.

5. **Interactive Elements**: Where appropriate, include:
   - Code examples (if technical)
   - Diagrams descriptions
   - Case studies
   - Exercise suggestions

6. **Summary**: Conclude with a concise summary highlighting the key takeaways.

7. **Further Reading**: Suggest additional resources for deeper learning.

Format the content using markdown with proper headings, bullet points, code blocks (where applicable), and emphasis.
Make it comprehensive, educational, and engaging for learners.
`, topicName, chapterName, subjectName, courseName)

	content, err := gh.GenerateContent(ctx, prompt)
	if err != nil {
		return "", err
	}

	// Process the content to handle special formatting
	processedContent := gh.ProcessMermaidContent(content)
	processedContent = gh.ExtractMarkdown(processedContent)

	return processedContent, nil
}

// ProcessMermaidContent processes mermaid diagrams in the content
func (gh *GeminiHelper) ProcessMermaidContent(content string) string {
	// Find and replace mermaid code blocks
	mermaidRegex := regexp.MustCompile(`(?s)` + "`" + `{3}mermaid(.*?)` + "`" + `{3}`)
	
	return mermaidRegex.ReplaceAllStringFunc(content, func(match string) string {
		// Extract the content between ```mermaid and ```
		lines := strings.Split(match, "\n")
		if len(lines) < 2 {
			return match
		}
		
		// Remove the first line (```mermaid) and last line (```)
		mermaidContent := strings.Join(lines[1:len(lines)-1], "\n")
		return fmt.Sprintf(`<pre class="mermaid">%s</pre>`, mermaidContent)
	})
}

// ExtractMarkdown removes markdown wrapper if present
func (gh *GeminiHelper) ExtractMarkdown(content string) string {
	// Remove the first occurrence of ```markdown and last occurrence of ```
	if strings.Contains(content, "```markdown") {
		start := strings.Index(content, "```markdown")
		end := strings.LastIndex(content, "```")
		if start != -1 && end != -1 && end > start {
			return strings.TrimSpace(content[start+12 : end])
		}
	}
	return content
}

// ExtractSQLQuery extracts SQL query from response text
func (gh *GeminiHelper) ExtractSQLQuery(responseText string) (string, error) {
	// Find the start and end of the SQL block
	sqlStart := strings.Index(responseText, "```sql")
	if sqlStart == -1 {
		return "", fmt.Errorf("SQL block not found in the response")
	}
	sqlStart += 6 // Skip "```sql"

	sqlEnd := strings.Index(responseText[sqlStart:], "```")
	if sqlEnd == -1 {
		return "", fmt.Errorf("SQL block end not found in the response")
	}

	// Extract and clean the SQL query
	sqlQuery := strings.TrimSpace(responseText[sqlStart : sqlStart+sqlEnd])

	// Remove leading 'l' if present (cleanup from the Python implementation)
	if strings.HasPrefix(sqlQuery, "l") {
		sqlQuery = strings.TrimSpace(sqlQuery[1:])
	}

	return sqlQuery, nil
}

// GenerateImageWithText generates image based on descriptive prompt (for Gemini 2.0 models)
func (gh *GeminiHelper) GenerateImageWithText(ctx context.Context, prompt string) ([]byte, string, error) {
	if err := gh.InitClient(ctx); err != nil {
		return nil, "", err
	}
	defer gh.client.Close()

	config := &genai.GenerateContentConfig{
		ResponseModalities: []string{"TEXT", "IMAGE"},
	}

	result, err := gh.client.Models.GenerateContent(
		ctx,
		"gemini-2.0-flash-preview-image-generation", // Image generation model
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating image with text: %v", err)
		return nil, "", err
	}

	var imageBytes []byte
	var textResponse string

	for _, part := range result.Candidates[0].Content.Parts {
		if part.Text != "" {
			textResponse = part.Text
		} else if part.InlineData != nil {
			imageBytes = part.InlineData.Data
		}
	}

	return imageBytes, textResponse, nil
}